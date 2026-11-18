import { useEffect, useState } from "react";
import { api } from "./api/client";
import LoadingSpinner from "./components/LoadingSpinner";
import LoginScreen from "./components/LoginScreen";
import NewsSection from "./components/NewsSection";
import StockSelector from "./components/StockSelector";
import TimeRangeSelector from "./components/TimeRangeSelector";
import ArticleDetailModal from "./components/ArticleDetailModal";
import SourceHealthDashboard from "./components/SourceHealthDashboard";
import type { NewsResponse, Stock, TimeRange, ArticleRecord } from "./types/news";

function AppLogo() {
  return (
    <div className="flex items-center gap-2.5">
      <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm font-bold text-sm tracking-wider">
        BH
      </div>
      <div>
        <div className="flex items-center gap-1.5">
          <span className="text-slate-900 font-bold text-base tracking-tight">Borsel Handler</span>
          <span className="text-[11px] font-semibold text-blue-700 bg-blue-50 border border-blue-200 px-1.5 py-0.5 rounded">
            v2.0
          </span>
        </div>
        <p className="text-[11px] text-slate-500 font-medium">Indian Financial Market Intelligence & Data Engineering</p>
      </div>
    </div>
  );
}

export default function App() {
  // Authentication bypassed - direct access enabled
  const [authed, setAuthed] = useState(true);
  const [activeTab, setActiveTab] = useState<"feed" | "search" | "health">("feed");

  // Stock feed state
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState<string>("TCS");
  const [timerange, setTimerange] = useState<TimeRange>("48h");
  const [newsData, setNewsData] = useState<NewsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [feedFilter, setFeedFilter] = useState<string>("");

  // Archive search state
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<ArticleRecord[]>([]);
  const [searchTotal, setSearchTotal] = useState(0);
  const [searchLoading, setSearchLoading] = useState(false);

  // Detail Modal state
  const [selectedArticle, setSelectedArticle] = useState<ArticleRecord | null>(null);

  if (!authed) {
    return <LoginScreen onSuccess={() => setAuthed(true)} />;
  }

  useEffect(() => {
    api.getStocks().then((data) => {
      setStocks(data);
      if (data.length > 0 && !selectedSymbol) {
        setSelectedSymbol(data[0].symbol);
      }
    }).catch(console.error);
  }, []);

  useEffect(() => {
    if (selectedSymbol && activeTab === "feed") {
      handleFetch();
    }
  }, [selectedSymbol, timerange]);

  async function handleFetch(isRefresh = false) {
    if (!selectedSymbol) return;
    setLoading(true);
    setError(null);
    try {
      if (stocks.length === 0) {
        const stockList = await api.getStocks().catch(() => []);
        if (stockList.length > 0) {
          setStocks(stockList);
        }
      }
      const data = await api.getNews(selectedSymbol, timerange, isRefresh);
      setNewsData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function handleRetry() {
    setError(null);
    try {
      let currentSym = selectedSymbol;
      if (stocks.length === 0) {
        const data = await api.getStocks();
        setStocks(data);
        if (data.length > 0) {
          currentSym = currentSym || data[0].symbol;
          setSelectedSymbol(currentSym);
        }
      }
      if (currentSym) {
        setLoading(true);
        const data = await api.getNews(currentSym, timerange, false);
        setNewsData(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSearch() {
    if (!searchQuery.trim()) return;
    setSearchLoading(true);
    try {
      const res = await api.searchRecords(searchQuery);
      setSearchResults(res.items);
      setSearchTotal(res.total);
    } catch (err) {
      console.error("Search error", err);
    } finally {
      setSearchLoading(false);
    }
  }

  function handleExport(format: "csv" | "parquet", customQuery?: string) {
    const url = api.getExportUrl({
      format,
      symbol: activeTab === "feed" ? selectedSymbol : undefined,
      query: activeTab === "search" ? (customQuery ?? searchQuery) : undefined,
      limit: 1000,
    });
    window.open(url, "_blank");
  }

  const filterFeedItems = (items: NewsResponse["categories"]["direct"] = []) => {
    if (!feedFilter.trim()) return items;
    const q = feedFilter.toLowerCase().trim();
    return items.filter(
      (item) =>
        (item.title && item.title.toLowerCase().includes(q)) ||
        (item.snippet && item.snippet.toLowerCase().includes(q)) ||
        (item.source && item.source.toLowerCase().includes(q)) ||
        (item.why_it_matters && item.why_it_matters.toLowerCase().includes(q))
    );
  };

  const filteredDirect = newsData ? filterFeedItems(newsData.categories.direct) : [];
  const filteredSupplyChain = newsData ? filterFeedItems(newsData.categories.supply_chain) : [];
  const filteredMacro = newsData ? filterFeedItems(newsData.categories.macro) : [];
  const totalMatches = filteredDirect.length + filteredSupplyChain.length + filteredMacro.length;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-800">
      {/* ── Institutional Header (Light Theme) ── */}
      <header className="bg-white border-b border-slate-200 shadow-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <AppLogo />

          {/* Navigation Tabs */}
          <nav className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-slate-200">
            <button
              onClick={() => setActiveTab("feed")}
              className={`px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-colors flex items-center gap-1.5 ${
                activeTab === "feed"
                  ? "bg-white text-blue-700 shadow-sm"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
              </svg>
              Intelligence Feed
            </button>

            <button
              onClick={() => setActiveTab("search")}
              className={`px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-colors flex items-center gap-1.5 ${
                activeTab === "search"
                  ? "bg-white text-blue-700 shadow-sm"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              Historical Search
            </button>

            <button
              onClick={() => setActiveTab("health")}
              className={`px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-colors flex items-center gap-1.5 ${
                activeTab === "health"
                  ? "bg-white text-blue-700 shadow-sm"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              Source Health & Ops
            </button>
          </nav>
        </div>
      </header>

      {/* ── Main View Content ── */}
      <main className="max-w-7xl mx-auto px-6 py-6 flex-1 w-full">
        {/* Tab 1: Intelligence Feed */}
        {activeTab === "feed" && (
          <div className="space-y-6">
            {/* Controls Bar */}
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
              <div className="flex flex-wrap items-end justify-between gap-4">
                <div className="flex flex-wrap items-end gap-4">
                  <div className="flex flex-col gap-1.5">
                    <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Select Stock</label>
                    <StockSelector stocks={stocks} value={selectedSymbol} onChange={setSelectedSymbol} />
                  </div>

                  <div className="flex flex-col gap-1.5">
                    <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Time Window</label>
                    <TimeRangeSelector value={timerange} onChange={setTimerange} />
                  </div>
                </div>

                <div className="flex items-center gap-2.5">
                  <div className="flex items-center bg-slate-100 rounded-lg p-0.5 border border-slate-200 shadow-inner">
                    <button
                      type="button"
                      onClick={() => handleExport("csv")}
                      title="Export filtered records as CSV (formula sanitized)"
                      className="px-2.5 py-1.5 text-xs font-semibold text-slate-700 hover:text-emerald-700 hover:bg-white rounded-md transition-all flex items-center gap-1.5"
                    >
                      <svg className="w-3.5 h-3.5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      CSV
                    </button>
                    <button
                      type="button"
                      onClick={() => handleExport("parquet")}
                      title="Export filtered records as Apache Parquet for AI/Data modeling"
                      className="px-2.5 py-1.5 text-xs font-semibold text-slate-700 hover:text-purple-700 hover:bg-white rounded-md transition-all flex items-center gap-1.5"
                    >
                      <svg className="w-3.5 h-3.5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2 1.5 3 3.5 3h9c2 0 3.5-1 3.5-3V7c0-2-1.5-3-3.5-3h-9C5.5 4 4 5 4 7z" />
                      </svg>
                      Parquet
                    </button>
                  </div>

                  <button
                    type="button"
                    onClick={() => handleFetch(true)}
                    disabled={loading || !selectedSymbol}
                    className="px-4 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 rounded-lg transition-colors flex items-center gap-2 shadow-sm"
                  >
                    {loading ? <LoadingSpinner /> : (
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                    )}
                    Refresh Intelligence
                  </button>
                </div>
              </div>

              {/* Feed Real-Time Search Bar */}
              <div className="pt-3 border-t border-slate-100 flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
                <div className="relative flex-1">
                  <input
                    type="text"
                    value={feedFilter}
                    onChange={(e) => setFeedFilter(e.target.value)}
                    placeholder={`Search within ${selectedSymbol} feed (filter by headline, summary, source, or keywords)...`}
                    className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-8 py-2.5 text-slate-800 placeholder-slate-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                  />
                  <svg className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  {feedFilter && (
                    <button
                      type="button"
                      onClick={() => setFeedFilter("")}
                      className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600 p-0.5 rounded-full hover:bg-slate-200 transition-colors"
                      title="Clear search"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  )}
                </div>
                {feedFilter && (
                  <div className="flex items-center gap-2 self-end sm:self-auto shrink-0">
                    <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-blue-50 text-blue-700 border border-blue-200">
                      {totalMatches} matching article{totalMatches === 1 ? "" : "s"}
                    </span>
                    <button
                      type="button"
                      onClick={() => setFeedFilter("")}
                      className="text-xs text-slate-500 hover:text-slate-800 underline"
                    >
                      Clear
                    </button>
                  </div>
                )}
              </div>
            </div>

            {error && (
              <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 text-xs text-rose-700 flex items-center justify-between">
                <span>{error}</span>
                <button onClick={handleRetry} className="font-semibold underline ml-2 cursor-pointer hover:text-rose-900">Retry</button>
              </div>
            )}

            {loading && !newsData && (
              <div className="bg-white rounded-xl border border-slate-200 p-12 text-center shadow-sm">
                <LoadingSpinner stock={selectedSymbol} />
              </div>
            )}

            {newsData && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-bold text-slate-900">{newsData.stock.name} ({newsData.stock.symbol})</h2>
                    <p className="text-xs text-slate-500">
                      Sector: {newsData.stock.sector} · Found {newsData.total} items across sources
                      {feedFilter && (
                        <span className="ml-2 font-medium text-blue-700">({totalMatches} matching &ldquo;{feedFilter}&rdquo;)</span>
                      )}
                    </p>
                  </div>
                  <span className="text-[11px] font-semibold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-full border border-slate-200">
                    Fetched {new Date(newsData.fetched_at).toLocaleTimeString()}
                  </span>
                </div>

                {feedFilter && totalMatches === 0 ? (
                  <div className="bg-white border border-slate-200 rounded-xl p-8 text-center space-y-2 shadow-sm">
                    <p className="text-sm font-semibold text-slate-800">No articles match &ldquo;{feedFilter}&rdquo;</p>
                    <p className="text-xs text-slate-500">No headlines, summaries, or sources matched your query in this feed.</p>
                    <button
                      type="button"
                      onClick={() => setFeedFilter("")}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors border border-blue-200"
                    >
                      Clear search filter
                    </button>
                  </div>
                ) : (
                  <>
                    <NewsSection
                      category="direct"
                      items={filteredDirect}
                    />

                    <NewsSection
                      category="supply_chain"
                      items={filteredSupplyChain}
                    />

                    <NewsSection
                      category="macro"
                      items={filteredMacro}
                      isLast={true}
                    />
                  </>
                )}
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Historical Search & Archive */}
        {activeTab === "search" && (
          <div className="space-y-6">
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Historical Archive Search</h3>
                <p className="text-xs text-slate-500">Search across indexed news, exchange filings, RBI/SEBI circulars, and PIB policy releases.</p>
              </div>

              <div className="flex gap-3">
                <div className="relative flex-1">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                    placeholder="Enter keywords (e.g. 'dividend', 'merger', 'monetary policy', 'order win')..."
                    className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-3.5 py-2.5 text-slate-800 placeholder-slate-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                  />
                  <svg className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>

                <button
                  onClick={handleSearch}
                  disabled={searchLoading || !searchQuery.trim()}
                  className="px-5 py-2.5 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 rounded-lg transition-colors flex items-center gap-1.5"
                >
                  {searchLoading ? <LoadingSpinner /> : "Search Repository"}
                </button>
              </div>
            </div>

            {searchTotal > 0 && (
              <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
                <div>
                  Found <span className="font-bold text-slate-800">{searchTotal}</span> historical records
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="text-[11px] font-semibold text-slate-400 mr-1">Export:</span>
                  <button
                    onClick={() => handleExport("csv", searchQuery)}
                    className="px-2.5 py-1 text-[11px] font-semibold bg-white border border-slate-200 rounded text-slate-700 hover:text-emerald-700 hover:border-emerald-300 shadow-sm transition-all"
                  >
                    CSV
                  </button>
                  <button
                    onClick={() => handleExport("parquet", searchQuery)}
                    className="px-2.5 py-1 text-[11px] font-semibold bg-white border border-slate-200 rounded text-slate-700 hover:text-purple-700 hover:border-purple-300 shadow-sm transition-all"
                  >
                    Parquet
                  </button>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {searchResults.map((art) => (
                <div
                  key={art.id}
                  onClick={() => setSelectedArticle(art)}
                  className="bg-white p-5 rounded-xl border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all cursor-pointer space-y-2.5"
                >
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="font-semibold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                      {art.source_name}
                    </span>
                    <span className="text-slate-400">{new Date(art.published_at).toLocaleDateString()}</span>
                  </div>

                  <h4 className="text-sm font-semibold text-slate-900 leading-snug line-clamp-2">
                    {art.title}
                  </h4>

                  <p className="text-xs text-slate-600 leading-relaxed line-clamp-3">
                    {art.snippet}
                  </p>

                  <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-[11px]">
                    <span className="font-medium text-slate-500">
                      Category: {art.category.replace("_", " ")}
                    </span>
                    <span className="text-blue-600 font-semibold hover:underline">
                      View Provenance →
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {searchResults.length === 0 && !searchLoading && searchQuery && (
              <div className="bg-white rounded-xl border border-slate-200 p-12 text-center text-xs text-slate-400">
                No articles matching query "{searchQuery}". Try broader search terms.
              </div>
            )}
          </div>
        )}

        {/* Tab 3: Source Health & Ops */}
        {activeTab === "health" && (
          <SourceHealthDashboard />
        )}
      </main>

      {/* Article Detail Inspection Modal */}
      <ArticleDetailModal
        article={selectedArticle}
        onClose={() => setSelectedArticle(null)}
      />

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-4 px-6 text-center text-xs text-slate-400">
        Borsel Handler Intelligence Platform · Institutional Financial Data Engineering · Fully Idempotent Ingestion
      </footer>
    </div>
  );
}
