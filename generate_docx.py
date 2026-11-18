"""
Borsel Handler — Comprehensive Architecture & Scraping Technology Word Document Generator
Creates a professionally styled, publication-ready DOCX document.
"""

import sys
from datetime import datetime
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    """Sets background color of a table cell."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tc_pr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets internal padding for a cell in dxa (1 pt = 20 dxa)."""
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tc_pr.append(tc_mar)

def add_callout(doc, title, text, bg_color="F0F4F8", border_color="0052CC"):
    """Adds a stylish callout box with a colored left border."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    cell = tbl.rows[0].cells[0]
    cell.width = Inches(6.5)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=140)
    
    # Left border only
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:left w:val="single" w:sz="36" w:space="0" w:color="{border_color}"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tc_pr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    run_t = p.add_run(f"📌 {title}\n")
    run_t.bold = True
    run_t.font.name = "Arial"
    run_t.font.size = Pt(11)
    run_t.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
    
    run_b = p.add_run(text)
    run_b.font.name = "Arial"
    run_b.font.size = Pt(10)
    run_b.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    
    # Spacer
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(4)
    p_after.paragraph_format.space_after = Pt(6)

def style_heading_1(p, text):
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(16)
    run.bold = True
    run.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

def style_heading_2(p, text):
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(13)
    run.bold = True
    run.font.color.rgb = RGBColor(0x00, 0x66, 0x99)

def style_heading_3(p, text):
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(11.5)
    run.bold = True
    run.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)

def add_body_p(doc, text, bold_prefix="", space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Arial"
        r_pre.font.size = Pt(10.5)
        r_pre.bold = True
        r_pre.font.color.rgb = RGBColor(0x11, 0x18, 0x27)
    r_body = p.add_run(text)
    r_body.font.name = "Arial"
    r_body.font.size = Pt(10.5)
    r_body.font.color.rgb = RGBColor(0x2B, 0x2B, 0x2B)
    return p

def add_bullet_p(doc, bold_prefix, text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix + ": ")
        r_pre.font.name = "Arial"
        r_pre.font.size = Pt(10)
        r_pre.bold = True
        r_pre.font.color.rgb = RGBColor(0x11, 0x18, 0x27)
    r_body = p.add_run(text)
    r_body.font.name = "Arial"
    r_body.font.size = Pt(10)
    r_body.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    return p

def create_table(doc, headers, data, col_widths=None):
    """Creates a sleek corporate table with dark blue headers and alternate rows."""
    tbl = doc.add_table(rows=len(data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False

    # Header Row
    hdr_row = tbl.rows[0]
    for idx, header_text in enumerate(headers):
        cell = hdr_row.cells[idx]
        if col_widths and idx < len(col_widths):
            cell.width = col_widths[idx]
        set_cell_background(cell, "003366")
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(header_text)
        r.font.name = "Arial"
        r.font.size = Pt(10)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # Data Rows
    for r_idx, row_values in enumerate(data):
        row = tbl.rows[r_idx + 1]
        bg = "F9FAFB" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_values):
            cell = row.cells[c_idx]
            if col_widths and c_idx < len(col_widths):
                cell.width = col_widths[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(str(val))
            r.font.name = "Arial"
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    # Add space after table
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(6)
    p_sp.paragraph_format.space_after = Pt(6)
    return tbl


def main():
    doc = docx.Document()

    # Configure Margins: 0.8 inch all around
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # =========================================================================
    # DOCUMENT COVER / TITLE HEADER
    # =========================================================================
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(4)
    run_title = p_title.add_run("⚡ Borsel Handler")
    run_title.font.name = "Arial"
    run_title.font.size = Pt(26)
    run_title.bold = True
    run_title.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(8)
    run_sub = p_sub.add_run("Institutional Financial Intelligence, Market Data Engineering & Automated Scraping Architecture")
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(13)
    run_sub.font.color.rgb = RGBColor(0x00, 0x66, 0x99)
    run_sub.bold = True

    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_before = Pt(0)
    p_meta.paragraph_format.space_after = Pt(14)
    run_meta = p_meta.add_run("Comprehensive Technical Dossier | Covers Ingestion, Scraping Protocols, Deduplication, Entity Resolution, Storage & UI")
    run_meta.font.name = "Arial"
    run_meta.font.size = Pt(9.5)
    run_meta.font.italic = True
    run_meta.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    add_callout(
        doc,
        "System Purpose at a Glance",
        "Borsel Handler is an institutional-grade financial data engineering and real-time intelligence platform. "
        "It autonomously harvests, normalizes, resolves, classifies, and deduplicates corporate disclosures, regulatory orders, "
        "and financial journalism across NSE, BSE, RBI, SEBI, PIB, and 14 premier Indian business publications. It transforms "
        "chaotic financial text into deterministic datasets stored simultaneously in PostgreSQL (for low-latency operational queries) "
        "and Apache Parquet (for quantitative backtesting and LLM Financial RAG context windows)."
    )

    # =========================================================================
    # SECTION 1: EXECUTIVE SUMMARY & PROBLEM STATEMENT
    # =========================================================================
    style_heading_1(doc.add_paragraph(), "1. Executive Summary & Industry Problem Statement")
    
    add_body_p(
        doc,
        "The Indian capital market ecosystem is one of the most vibrant and rapidly growing globally. Every day, thousands of "
        "corporate announcements, regulatory circulars, and news stories are emitted across highly fragmented, heterogeneous portals "
        "(NSE India, BSE India, Reserve Bank of India, SEBI, Press Information Bureau, and national business newspapers). "
        "For quantitative hedge funds, algorithmic trading desks, risk managers, and LLM-driven research teams, this raw flow presents "
        "four severe architectural challenges:"
    )

    add_bullet_p(doc, "High Syndication & Duplicate Clutter", "Up to 60-70% of financial news across portals consists of identical or lightly rephrased syndicated wire stories (e.g., PTI, ANI, Bloomberg syndications republishing the same headline across 8 news portals).")
    add_bullet_p(doc, "Entity Ambiguity & Subword Collisions", "Corporate press releases often use colloquial brand names ('Tata Motors', 'L&T', 'Westside') rather than standardized stock tickers ('TATAMOTORS', 'LT', 'TRENT'). Simple substring searches yield dangerous false positives (e.g., matching the word 'it' or 'on' as an equity ticker).")
    add_bullet_p(doc, "Fragile & Heterogeneous Ingestion Endpoints", "Indian exchange portals frequently shift DOM structures, enforce anti-scraping firewalls, utilize session cookies, or rely on JavaScript hydration, breaking standard naive scraping scripts.")
    add_bullet_p(doc, "Relational vs. Vector/Columnar Analytical Divide", "Relational databases (PostgreSQL/MySQL) are ideal for operational queries and transactional dashboards but inefficient for vector indexing, pandas/Polars DataFrame manipulation, and vectorized historical backtesting.")

    add_body_p(
        doc,
        "Borsel Handler resolves these challenges through a unified, production-hardened data engineering pipeline combining "
        "robust async HTTP collectors, an optional headless browser fallback (Playwright), a 6-tier deduplication engine, "
        "deterministic word-boundary entity resolution, and a dual-tier storage strategy (PostgreSQL + Apache Parquet)."
    )

    # =========================================================================
    # SECTION 2: HIGH-LEVEL ARCHITECTURE & SUBSYSTEMS
    # =========================================================================
    style_heading_1(doc.add_paragraph(), "2. End-to-End System Architecture")

    add_body_p(
        doc,
        "Borsel Handler is engineered as four decoupled, modular subsystems ensuring maximum testability, zero downtime, "
        "and resilience against external source failures:"
    )

    arch_table_headers = ["Subsystem", "Primary Modules", "Core Responsibilities & Capabilities"]
    arch_table_data = [
        [
            "1. Multi-Channel Ingestion Layer",
            "borsel_handler.collectors.*\n(nse, bse, rbi, sebi, pib, rss, playwright)",
            "Asynchronous polling of NSE, BSE, RBI, SEBI, PIB, and 14 financial media RSS feeds. Manages cookie-handshakes, DOM extraction, and polite rate limits."
        ],
        [
            "2. Data Engineering & Processing Pipeline",
            "borsel_handler.core.html_utils\nborsel_handler.data.resolver\nborsel_handler.classification\nborsel_handler.dedup",
            "HTML sanitization, canonical URL normalization, UTC timestamp parsing, word-boundary entity resolution against listed Indian equities, 14-class taxonomy tagging, and 6-tier deduplication."
        ],
        [
            "3. Dual-Tier Storage Layer",
            "borsel_handler.storage.*\n(database, models, repository)\nApache Parquet via PyArrow",
            "Dual-dialect SQLAlchemy 2.0 ORM (PostgreSQL in production, SQLite in local dev/testing). High-throughput Snappy-compressed Apache Parquet exports for LLM context and Quant DataFrames."
        ],
        [
            "4. Application & Delivery Layer",
            "borsel_handler.api.*\nfrontend/* (React 19, Vite 8, Tailwind v4)",
            "FastAPI REST gateway with interactive OpenAPI docs, live source health telemetry, CWE-1236 safe CSV/Parquet export, and institutional light cobalt dashboard."
        ],
    ]
    create_table(doc, arch_table_headers, arch_table_data, [Inches(1.8), Inches(2.2), Inches(2.5)])

    # =========================================================================
    # SECTION 3: INGESTION & WEB SCRAPING TECHNOLOGIES
    # =========================================================================
    style_heading_1(doc.add_paragraph(), "3. Web Scraping & Ingestion Technology Stack")

    add_body_p(
        doc,
        "Data collection in Borsel Handler is designed with strict adherence to non-evasive compliance, high throughput, "
        "and deterministic resilience. Below are the key technologies and frameworks utilized for scraping and data collection:"
    )

    style_heading_2(doc.add_paragraph(), "3.1 Asynchronous HTTP Client: HTTPX (Python)")
    add_body_p(
        doc,
        "Unlike synchronous libraries like `requests` or `urllib2`, Borsel Handler is powered by `httpx.AsyncClient`. "
        "This enables non-blocking, concurrent retrieval across dozens of remote endpoints without spawning heavy OS threads."
    )
    add_bullet_p(doc, "Connection Pooling & Keep-Alive", "Maintains persistent TCP connections, dramatically reducing SSL/TLS handshake latency when polling exchange servers.")
    add_bullet_p(doc, "Cookie-Priming Handshake", "Required for endpoints like NSE India that validate incoming requests with session cookies (e.g. `ak_bmsc`). The collector first visits the portal homepage to gather valid session tokens before hitting JSON endpoints.")
    add_bullet_p(doc, "Custom Institutional User-Agents", "Dispatches standard, honest browser headers (`Mozilla/5.0 ... Chrome/124.0.0.0 Safari/537.36 BorselHandler/1.0`) with proper Referer, Accept, and Accept-Language headers.")
    add_bullet_p(doc, "Strict Timeout Bounding", "Enforces configurable connect and read timeouts (10-20 seconds) to prevent frozen sockets from degrading the entire pipeline.")

    style_heading_2(doc.add_paragraph(), "3.2 Dynamic Headless Browser Engine: Playwright (Headless Chromium)")
    add_body_p(
        doc,
        "Certain regulatory notices and modern corporate portal announcements rely on Single Page Applications (SPAs) "
        "or client-side JavaScript hydration (e.g., React, Angular, or Vue rendering) where raw HTML contains empty root containers (`<div id='root'></div>`)."
    )
    add_bullet_p(doc, "Headless Chromium Automation", "Playwright launches an isolated Chromium browser instance (`headless=True`) with arguments `--no-sandbox`, `--disable-gpu`, and `--disable-dev-shm-usage`.")
    add_bullet_p(doc, "Strict Bounded Execution", "Execution is bounded by a strict 30-second timeout. Contexts and browser instances are deterministically closed in `finally` blocks to guarantee zero memory leakage.")
    add_bullet_p(doc, "Optional & Non-Breaking Design", "Playwright is completely optional. If Playwright is not installed in the host environment, Borsel Handler gracefully logs an informational message and skips dynamic rendering without halting the core pipeline.")
    add_bullet_p(doc, "Network Idle State Detection", "Waits for `wait_until='networkidle'` before capturing rendered DOM via `page.content()`, ensuring that dynamic AJAX calls have populated the announcement tables.")

    style_heading_2(doc.add_paragraph(), "3.3 DOM Extraction & Parsing: BeautifulSoup4 and LXML")
    add_body_p(
        doc,
        "Once raw or rendered HTML payloads are received, `BeautifulSoup4` coupled with the high-performance C-accelerated `lxml` parser "
        "handles structural tag navigation and content extraction:"
    )
    add_bullet_p(doc, "Targeted CSS Selector Queries", "Extracts candidate disclosures via `.announcement-item`, `.news-card`, `article`, `tr.announcement`, and headline links.")
    add_bullet_p(doc, "Robust Text Sanitization (`clean_html_to_text`)", "Strips script, style, navigation, and advertisement boilerplate. Normalizes whitespace, unescapes HTML entities (`&amp;` -> `&`, `&quot;` -> `\"`), and truncates clean snippets without cutting mid-word.")
    add_bullet_p(doc, "Relative-to-Absolute Link Transformation", "Resolves relative href attributes (e.g., `/corporates/ann/doc.pdf`) against source base URLs into fully qualified, clickable HTTPS URLs.")

    style_heading_2(doc.add_paragraph(), "3.4 Syndicated Feed Ingestion: Feedparser")
    add_body_p(
        doc,
        "Used for ingesting XML, RSS 2.0, and Atom 1.0 feeds from regulatory bodies and top business newspapers."
    )
    add_bullet_p(doc, "Standardized Payload Parsing", "Seamlessly extracts `title`, `summary`/`description`, `published_parsed`, `link`, and feed metadata.")
    add_bullet_p(doc, "Fault-Tolerant XML Handling", "Tolerates malformed XML characters and CDATA wrappers frequently found in legacy RSS feeds without throwing unhandled parse exceptions.")

    style_heading_2(doc.add_paragraph(), "3.5 URL Canonicalization & Parameter Scrubbing (`url_utils.py`)")
    add_body_p(
        doc,
        "Marketing parameters and session tags artificially inflate duplicate counts. Borsel Handler enforces strict URL canonicalization:"
    )
    add_bullet_p(doc, "Query Parameter Stripping", "Removes `utm_source`, `utm_medium`, `utm_campaign`, `ref`, `fbclid`, `gclid`, and session identifiers.")
    add_bullet_p(doc, "Protocol & Case Normalization", "Converts schemes and domain names to lowercase, standardizes HTTPS, removes trailing slashes, and eliminates default ports.")

    style_heading_2(doc.add_paragraph(), "3.6 Temporal Normalization (`dateutil` & UTC Standardization)")
    add_body_p(
        doc,
        "Different financial portals emit timestamps in wildly diverse formats (e.g., '28-Jun-2026 15:30:00', '2026-06-28T10:00:00Z', RFC 2822, or Indian Standard Time IST without timezone offsets). "
        "The normalization layer converts all parsed timestamps into timezone-aware UTC ISO-8601 datetimes, ensuring consistent time-series analysis."
    )

    # =========================================================================
    # SECTION 4: DATA SOURCES & HARVESTING SPECIFICATIONS
    # =========================================================================
    style_heading_1(doc.add_paragraph(), "4. Data Sources & Scraping Protocols Coverage")

    add_body_p(
        doc,
        "Borsel Handler monitors six distinct classes of financial and regulatory intelligence channels. "
        "Each channel features a dedicated collector implementing the standardized `BaseCollector` interface:"
    )

    sources_headers = ["Channel / Source", "Protocol & Mechanism", "Data Harvested", "Attachment & Linking"]
    sources_data = [
        [
            "NSE India (Equities & SME)",
            "HTTP REST API + Cookie Priming\nEndpoint: /api/corporate-announcements",
            "Exchange filings, financial results, board meetings, insider trading, SME platform disclosures.",
            "Resolves PDF archive attachments via https://nsearchives.nseindia.com/corporate/"
        ],
        [
            "BSE India Corporate Announcements",
            "HTTP REST API + Scrip Mapping\nEndpoint: /BseIndiaAPI/api/AnnSubCategoryGetData/w",
            "Corporate actions, dividend declarations, credit rating revisions, press releases.",
            "Constructs live PDF attachment links via https://www.bseindia.com/xml-data/corpfiling/AttachLive/"
        ],
        [
            "Reserve Bank of India (RBI)",
            "Dual-Channel: HTML Scraping + RSS\nBS_PressReleaseDisplay.aspx & rss_pressrelease.xml",
            "Monetary policy announcements, repo rate decisions, bank regulatory circulars, foreign exchange directives.",
            "Direct links to official RBI circular documents and press statements."
        ],
        [
            "Securities and Exchange Board of India (SEBI)",
            "Official RSS & XML Notification Feeds\nEndpoint: /sebirss.xml",
            "Regulatory orders, adjudication notices, mutual fund circulars, insider trading enforcement orders.",
            "Direct links to official SEBI PDF regulatory orders."
        ],
        [
            "Press Information Bureau (PIB)",
            "HTML Category Scraping + Keyword Filter\nEndpoint: /AllRelease.aspx?reg=3&lang=1",
            "Cabinet Committee on Economic Affairs (CCEA), Ministry of Finance, GST Council, PLI schemes, disinvestment.",
            "Official Government of India press communiqués."
        ],
        [
            "14x Tier-1 Financial Media Feeds",
            "Parallel Asynchronous RSS Collectors\n(ET, Mint, BS, FE, Moneycontrol, NDTV, CNBC)",
            "Breaking market news, sectoral analysis, macro indicators, broker consensus, earnings reviews.",
            "Canonical publisher story URLs."
        ],
    ]
    create_table(doc, sources_headers, sources_data, [Inches(1.8), Inches(2.0), Inches(2.0), Inches(1.7)])

    # =========================================================================
    # SECTION 5: ENTITY RESOLUTION, TAXONOMY & 6-TIER DEDUPLICATION
    # =========================================================================
    style_heading_1(doc.add_paragraph(), "5. Data Engineering & Processing Intelligence")

    style_heading_2(doc.add_paragraph(), "5.1 Deterministic Entity Resolution Engine (`resolver.py`)")
    add_body_p(
        doc,
        "Converting unstructured text into structured market data requires accurate attribution to listed equities. "
        "Borsel Handler's `CompanyResolver` operates using strict word boundaries to eliminate false positives:"
    )
    add_bullet_p(doc, r"Strict Word Boundaries (\b...\b)", "Prevents substring collisions (e.g. word 'continuation' matching ticker 'ON', or 'without' matching 'IT').")
    add_bullet_p(doc, "Curated Ambiguity Blocklist", "Tokens like `IT`, `ON`, `BE`, `AT`, `OR`, `IN`, `LT`, `TITAN`, `TRENT` require explicit contextual aliases before matching.")
    add_bullet_p(doc, "Special Brand Aliases", "Maps colloquial brand identities to official exchange symbols (e.g., 'Westside' / 'Zudio' -> `TRENT`, 'RIL' -> `RELIANCE`, 'State Bank' -> `SBIN`, 'L&T' -> `LT`).")
    add_bullet_p(doc, "Hierarchical Sector Taxonomy", "Automatically maps identified equities to standard institutional sectors (Information Technology, Banking & Financial Services, Automotive & Manufacturing, Healthcare, Energy, Metals & Mining, FMCG).")

    style_heading_2(doc.add_paragraph(), "5.2 14-Class Financial Event Classifier (`classifier.py`)")
    add_body_p(
        doc,
        "Every incoming disclosure or news item is classified into one of 14 deterministic financial categories using a weighted keyword engine:"
    )
    add_bullet_p(doc, "Financial & Earnings Results", "Quarterly/annual financial results, EBITDA, net profit, revenue growth.")
    add_bullet_p(doc, "Corporate Actions & Dividends", "Interim/final dividends, stock splits, bonus shares, rights issues.")
    add_bullet_p(doc, "Mergers, Acquisitions & Restructuring", "Takeovers, demergers, asset sales, strategic buyouts.")
    add_bullet_p(doc, "Fundraising & Capital Markets", "IPOs, Qualified Institutional Placements (QIP), preferential allotments, debt issues.")
    add_bullet_p(doc, "Regulatory & Monetary Policy", "RBI policy circulars, SEBI enforcement orders, banking guidelines.")
    add_bullet_p(doc, "Economic & Government Policies", "GST Council notifications, Cabinet approvals, fiscal budget updates.")
    add_bullet_p(doc, "Contracts, Orders & Partnerships", "Order wins, EPC project execution, strategic joint ventures.")

    style_heading_2(doc.add_paragraph(), "5.3 The 6-Tier Deduplication Engine (`engine.py`)")
    add_body_p(
        doc,
        "To eliminate duplicate and syndicated wire clutter, Borsel Handler executes a 6-stage hierarchical deduplication check "
        "before persisting any record to the primary database:"
    )

    dedup_headers = ["Tier Level", "Deduplication Strategy", "Mechanism & Logic", "Impact / Target Duplicate Type"]
    dedup_data = [
        [
            "Tier 1",
            "Exact Source Record ID",
            "Checks if (source_name, source_record_id) exists in database.",
            "Catches repeated poll cycles on the same API or RSS entry."
        ],
        [
            "Tier 2",
            "Canonical URL Match",
            "Matches sanitized, tracking-free canonical URL.",
            "Eliminates duplicate submissions pointing to identical destination articles."
        ],
        [
            "Tier 3",
            "SHA-256 Record Hash Match",
            "Generates SHA-256 fingerprint: hash(clean_title | symbol | YYYY-MM-DD-HH).",
            "Catches identical headlines emitted within the same 1-hour temporal window."
        ],
        [
            "Tier 4",
            "Cross-Source Token Jaccard Similarity",
            "Computes Jaccard word-token intersection over union (threshold >= 0.85 within +/- 12 hours).",
            "Identifies syndicated wire releases republished across competing newspapers (e.g. PTI news wires)."
        ],
        [
            "Tier 5",
            "Normalized Title Window Match",
            "Exact normalized title match within a +/- 24-hour publication window.",
            "Catches delayed cross-portal republications."
        ],
        [
            "Tier 6",
            "Normalized URL Variant Match",
            "Cleans original source URL variations (trailing slashes, default ports, protocols).",
            "Catches minor URL variations from different aggregator links."
        ],
    ]
    create_table(doc, dedup_headers, dedup_data, [Inches(1.2), Inches(1.8), Inches(2.2), Inches(2.3)])

    add_body_p(
        doc,
        "Audit Provenance: When a duplicate is detected, Borsel Handler does not silently discard it. "
        "Instead, it records a link in the `article_duplicates` table capturing the parent article ID, duplicate source, "
        "and deduplication reason, preserving complete forensic auditability."
    )

    # =========================================================================
    # SECTION 6: STORAGE SUBSYSTEM & QUANT/AI INTEGRATION
    # =========================================================================
    style_heading_1(doc.add_paragraph(), "6. Dual-Tier Storage & Quant / LLM Integration")

    add_body_p(
        doc,
        "Modern financial AI systems require two fundamentally different storage characteristics: low-latency relational queries "
        "for transactional user interfaces, and high-throughput columnar vector datasets for quantitative backtesting and LLM Retrieval-Augmented Generation (RAG)."
    )

    style_heading_2(doc.add_paragraph(), "6.1 Relational Store: PostgreSQL (Production) / SQLite (Development)")
    add_bullet_p(doc, "Dialect-Agnostic SQLAlchemy 2.0 ORM", "Seamlessly runs on SQLite for rapid zero-dependency local testing and PostgreSQL 14-18 for enterprise deployment.")
    add_bullet_p(doc, "Alembic Database Migrations", "Strict schema version control allowing seamless schema upgrades without data corruption.")
    add_bullet_p(doc, "Normalized Architecture", "Maintains isolated entities: `sources`, `articles`, `companies`, `categories`, `article_duplicates`, and `collection_runs`.")

    style_heading_2(doc.add_paragraph(), "6.2 Analytical Columnar Store: Apache Parquet (PyArrow & Polars)")
    add_bullet_p(doc, "High-Throughput Vectorized Storage", "Compressed using Google Snappy compression, yielding up to 80% smaller file footprints compared to CSV or JSON.")
    add_bullet_p(doc, "Instant DataFrame Ingestion", "Financial analysts can load millions of historical records directly into Pandas, Polars, or DuckDB in milliseconds.")
    add_bullet_p(doc, "LLM Financial RAG Ready", "Pre-structured for embedding generation with LangChain, LlamaIndex, or OpenAI/Google embeddings, providing clean context windows without HTML noise.")

    # =========================================================================
    # SECTION 7: API, AUTOMATION & FRONTEND DASHBOARD
    # =========================================================================
    style_heading_1(doc.add_paragraph(), "7. REST API Gateway, Automation & Financial UI")

    style_heading_2(doc.add_paragraph(), "7.1 FastAPI REST Gateway")
    add_bullet_p(doc, "Endpoints", "Comprehensive suite: `/api/v1/records`, `/api/v1/sources`, `/api/v1/stats`, `/api/v1/ingest/trigger`, `/api/v1/export`.")
    add_bullet_p(doc, "Spreadsheet Formula Hardening (CWE-1236)", "All exported CSV files sanitize fields starting with `=`, `+`, `-`, or `@` by prepending a single quote, neutralizing formula injection vulnerabilities in Microsoft Excel.")
    add_bullet_p(doc, "Interactive OpenAPI / Swagger Documentation", "Built-in interactive exploration at `http://localhost:8000/docs`.")

    style_heading_2(doc.add_paragraph(), "7.2 Background Ingestion Automation")
    add_bullet_p(doc, "Dual Schedule Engine", "Triggers an automatic live collection burst 5 seconds after application boot, followed by a recurring collection cycle every 60 minutes.")
    add_bullet_p(doc, "Non-Blocking Async Execution", "Runs completely in the background via FastAPI lifecycle handlers, never stalling user requests.")

    style_heading_2(doc.add_paragraph(), "7.3 React 19 Financial Dashboard")
    add_bullet_p(doc, "Modern Frontend Stack", "React 19, TypeScript, Vite 8, Tailwind CSS v4.")
    add_bullet_p(doc, "Design Aesthetic", "Institutional light white and cobalt blue palette designed for trading desks.")
    add_bullet_p(doc, "Telemetry & Features", "Live source health monitoring, manual ingest triggers, full-text search, sector/company filtering, and one-click CSV/Parquet downloads.")

    # =========================================================================
    # SECTION 8: VERIFICATION, TESTING & METRICS
    # =========================================================================
    style_heading_1(doc.add_paragraph(), "8. Empirical Verification & Quality Assurance")

    add_body_p(
        doc,
        "Borsel Handler was validated through an extensive test suite and an empirical live data ingestion audit:"
    )
    add_bullet_p(doc, "105 Automated Tests (100% Pass)", "Unit, integration, and end-to-end tests covering collectors, entity resolution, classification, deduplication tiers, and API routes.")
    add_bullet_p(doc, "Zero Network Dependency in CI", "All tests execute against local mock fixtures and recorded JSON/XML payloads, guaranteeing 100% deterministic CI runs.")
    add_bullet_p(doc, "Empirically Verified Live Ingestion", "Audited with 977+ live records collected from NSE, BSE, RBI, SEBI, PIB, and financial news wires with zero unhandled exceptions.")

    # =========================================================================
    # SECTION 9: SUMMARY & CONCLUSION
    # =========================================================================
    style_heading_1(doc.add_paragraph(), "9. Summary & Conclusion")
    add_body_p(
        doc,
        "Borsel Handler bridges the gap between chaotic, fragmented financial portals and high-performance quantitative/AI systems. "
        "By pairing resilient, compliant scraping engines with intelligent deduplication, entity resolution, and dual relational/columnar storage, "
        "it delivers institutional-grade market data engineering tailored for the modern Indian capital markets."
    )

    # Save document
    output_filename = "Borsel_Handler_Project_Explanation_and_Scraping_Architecture.docx"
    doc.save(output_filename)
    print(f"Document successfully created and saved as: {output_filename}")

if __name__ == "__main__":
    main()
