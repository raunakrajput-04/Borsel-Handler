"""
Asynchronous Ingestion Runner and Background Task Scheduler
Implements Section 13 of Mega Prompt 2:
- Coordinates all 7 source collectors (RSS, BSE, NSE Equities/SME, RBI, SEBI, PIB)
- Exponential backoff with random jitter for resilient network retrieval
- Prevents overlapping concurrent collection jobs via atomic lock
- Complete execution auditing and fault isolation
"""
import asyncio
import logging
import random
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from borsel_handler.collectors.base import BaseCollector
from borsel_handler.collectors.rss import RSSCollector
from borsel_handler.collectors.bse import BSEAnnouncementCollector
from borsel_handler.collectors.nse import NSEAnnouncementCollector
from borsel_handler.collectors.rbi import RBICollector
from borsel_handler.collectors.sebi import SEBICollector
from borsel_handler.collectors.pib import PIBCollector
from borsel_handler.core.models import CollectionRunSummary
from borsel_handler.storage.database import SessionLocal
from borsel_handler.storage.repository import NewsRepository

logger = logging.getLogger(__name__)


async def execute_with_retry(
    collector: BaseCollector,
    cutoff: Optional[datetime],
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> list:
    """
    Executes collector.fetch with exponential backoff and jitter.
    Formula: wait = min(max_delay, base_delay * 2^attempt + uniform(0, 1))
    """
    attempt = 0
    while attempt < max_retries:
        try:
            return await collector.fetch(cutoff=cutoff)
        except Exception as exc:
            attempt += 1
            if attempt >= max_retries:
                logger.error(
                    "Collector %s failed after %d retries: %s",
                    collector.source_name, max_retries, exc
                )
                raise
            jitter = random.uniform(0.1, 1.0)
            delay = min(15.0, (base_delay * (2 ** (attempt - 1))) + jitter)
            logger.warning(
                "Collector %s error: %s. Retrying attempt %d in %.2fs",
                collector.source_name, exc, attempt + 1, delay
            )
            await asyncio.sleep(delay)
    return []


class CollectionRunner:
    """Coordinates data collection, deduplication, and persistence across all sources."""

    _is_running = False
    _lock = asyncio.Lock()

    def __init__(self, collectors: Optional[List[BaseCollector]] = None):
        self.collectors = collectors or [
            RSSCollector(),
            BSEAnnouncementCollector(),
            NSEAnnouncementCollector(index_tag="equities"),
            NSEAnnouncementCollector(index_tag="sme"),
            RBICollector(),
            SEBICollector(),
            PIBCollector(),
        ]

    async def run_collector(
        self, collector: BaseCollector, db: Optional[Session] = None, cutoff_hours: int = 48
    ) -> CollectionRunSummary:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=cutoff_hours)
        started_at = datetime.now(timezone.utc)

        found = 0
        inserted = 0
        duplicates = 0
        error_msg = None
        status = "success"

        try:
            records = await execute_with_retry(collector, cutoff=cutoff)
            found = len(records)
        except Exception as exc:
            status = "failed"
            error_msg = str(exc)
            logger.error("Collection failed for %s: %s", collector.source_name, exc)
            records = []

        # Use a short scoped session for writing results to avoid holding database locks across network I/O
        owns_db = db is None
        session = db if db is not None else SessionLocal()
        try:
            log = NewsRepository.start_log(session, collector.source_name)
            for rec in records:
                _, is_ins, skip_reason = NewsRepository.insert_record(session, rec)
                if is_ins:
                    inserted += 1
                else:
                    duplicates += 1

            NewsRepository.finish_log(
                session, log.id, status, found, inserted, duplicates, error_msg
            )
        finally:
            if owns_db:
                session.close()

        return CollectionRunSummary(
            source_name=collector.source_name,
            status=status,
            items_found=found,
            items_inserted=inserted,
            items_duplicate=duplicates,
            error_message=error_msg,
            started_at=started_at,
            finished_at=datetime.now(timezone.utc),
        )

    async def run_all(self, cutoff_hours: int = 48) -> List[CollectionRunSummary]:
        """
        Executes all registered collectors sequentially or with fault isolation.
        Guarantees that overlapping runs are rejected.
        """
        if CollectionRunner._is_running:
            logger.warning("Collection job already in progress; skipping overlapping trigger.")
            return []

        async with CollectionRunner._lock:
            CollectionRunner._is_running = True
            summaries: List[CollectionRunSummary] = []
            try:
                for collector in self.collectors:
                    summary = await self.run_collector(collector, db=None, cutoff_hours=cutoff_hours)
                    summaries.append(summary)
            finally:
                CollectionRunner._is_running = False
            return summaries
