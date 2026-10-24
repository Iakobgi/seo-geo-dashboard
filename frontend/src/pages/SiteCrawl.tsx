import { useState } from "react";
import { Link } from "react-router-dom";
import { Download, Network, Loader2, ExternalLink } from "lucide-react";
import { crawlApi, type CrawlResult } from "../api/endpoints";
import { downloadFile, errorMessage, normalizeUrl } from "../api/helpers";
import { Empty, Notice, PageHeading } from "../components/UI";
import { csvCell, duplicateUrls, pageIssues } from "../utils/siteTools";
export default function SiteCrawl() {
  const [url, setUrl] = useState("");
  const [limit, setLimit] = useState(10);
  const [result, setResult] = useState<CrawlResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState("all");
  const [query, setQuery] = useState("");
  const run = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    let normalized: string;
    try {
      normalized = normalizeUrl(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Check the URL.");
      return;
    }
    setBusy(true);
    setResult(null);
    setFilter("all");
    setQuery("");
    try {
      setResult((await crawlApi.run(normalized, limit)).data);
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setBusy(false);
    }
  };
  const duplicates = result ? duplicateUrls(result) : new Set<string>();
  const pages =
    result?.pages.filter(
      (p) =>
        `${p.url} ${p.title || ""}`
          .toLowerCase()
          .includes(query.toLowerCase()) &&
        (filter === "all" ||
          (filter === "issues" &&
            (pageIssues(p).length > 0 || duplicates.has(p.url))) ||
          (filter === "indexing" && p.noindex) ||
          (filter === "duplicates" && duplicates.has(p.url))),
    ) || [];
  const exportCsv = () => {
    if (!result) return;
    const rows: unknown[][] = [
      [
        "URL",
        "HTTP status",
        "Title",
        "Description",
        "H1",
        "Words",
        "Response seconds",
        "Noindex",
        "Canonical URL",
        "Checks to review",
      ],
    ];
    for (const p of pages)
      rows.push([
        p.url,
        p.status_code,
        p.title,
        p.meta_description,
        p.h1,
        p.word_count,
        p.load_time,
        p.noindex,
        p.canonical_url,
        pageIssues(p).join("; "),
      ]);
    downloadFile(
      "site-crawl.csv",
      rows.map((r) => r.map(csvCell).join(",")).join("\r\n"),
      "text/csv;charset=utf-8",
    );
  };
  return (
    <div className="space-y-6">
      <PageHeading
        title="Site crawl"
        description="Check linked pages for missing metadata, indexing directives, duplicate content labels, and crawl errors."
      />
      <form className="panel tools-form" onSubmit={run}>
        <label className="field tools-url">
          Starting URL
          <input
            type="text"
            inputMode="url"
            required
            placeholder="https://example.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={busy}
          />
        </label>
        <label className="field">
          Page limit
          <select
            className="search-input"
            aria-label="Page limit"
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            disabled={busy}
          >
            {[5, 10, 20].map((n) => (
              <option key={n} value={n}>
                {n} pages
              </option>
            ))}
          </select>
        </label>
        <button className="button button-dark" disabled={busy}>
          {busy ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <Network size={16} />
          )}{" "}
          {busy ? "Crawling..." : "Start crawl"}
        </button>
        <p className="tools-help">
          Follows links on the same site, up to two levels deep, and respects
          robots.txt. No AI credits used. Results are not saved to audit
          history.
        </p>
      </form>
      {busy && (
        <p role="status" className="tools-status">
          Fetching pages and checking metadata. This can take up to 150 seconds.
        </p>
      )}
      {error && <Notice>{error}</Notice>}
      {!result && !busy && !error && (
        <div className="panel">
          <Empty title="Check more than one page">
            Start a crawl to review linked pages together. For SEO and GEO
            scores, use{" "}
            <Link to="/audits" className="text-blue-600">
              Website audits
            </Link>
            .
          </Empty>
        </div>
      )}
      {result && (
        <>
          <div className="stat-grid">
            {[
              ["Pages fetched", result.pages_crawled],
              [
                "Pages to review",
                result.pages.filter(
                  (p) => pageIssues(p).length > 0 || duplicates.has(p.url),
                ).length,
              ],
              [
                "Duplicate groups",
                Object.keys(result.duplicate_titles).length +
                  Object.keys(result.duplicate_meta_descriptions).length,
              ],
              ["Failed URLs", result.broken_internal_links.length],
            ].map(([label, value]) => (
              <div className="stat-card" key={label}>
                <div>{label}</div>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
          <div className="panel tools-summary">
            <strong>{result.start_url}</strong>
            <span>{result.crawl_duration.toFixed(1)}s crawl duration</span>
            <span>
              robots.txt{" "}
              {result.robots_txt_found ? "retrieved" : "not retrieved"}
            </span>
            <span>{result.sitemap_urls.length} sitemap URLs discovered</span>
          </div>
          <section className="panel">
            <div className="table-toolbar">
              <div>
                <h2 className="panel-title">Crawled pages</h2>
                <p className="panel-subtitle">
                  Checks are review prompts; short content and noindex can be
                  intentional. Response time is not a Core Web Vitals
                  measurement.
                </p>
              </div>
              <button
                className="button button-secondary"
                onClick={exportCsv}
                disabled={!pages.length}
              >
                <Download size={15} />
                Export CSV
              </button>
            </div>
            <div className="tools-filters">
              <input
                className="search-input"
                aria-label="Search crawled pages"
                placeholder="Search URL or title"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <select
                className="search-input"
                aria-label="Filter crawled pages"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
              >
                <option value="all">All pages</option>
                <option value="issues">Needs review</option>
                <option value="indexing">Noindex pages</option>
                <option value="duplicates">Duplicate metadata</option>
              </select>
              <span>{pages.length} results</span>
            </div>
            {pages.length ? (
              <div className="table-scroll">
                <table className="data-table crawl-table">
                  <thead>
                    <tr>
                      <th>Page</th>
                      <th>HTTP</th>
                      <th>Words</th>
                      <th>Response</th>
                      <th>Checks to review</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pages.map((p) => (
                      <tr key={p.url}>
                        <td>
                          <a
                            href={p.url}
                            target="_blank"
                            rel="noreferrer"
                            className="tools-page-link"
                          >
                            {p.title || "Untitled page"}{" "}
                            <ExternalLink size={11} />
                          </a>
                          <small>{p.url}</small>
                          <small>
                            {p.canonical_url
                              ? `Canonical: ${p.canonical_url}`
                              : "No canonical URL found"}
                          </small>
                        </td>
                        <td>{p.status_code ?? "No response"}</td>
                        <td>{p.word_count}</td>
                        <td>
                          {p.load_time === null
                            ? "Unavailable"
                            : `${p.load_time.toFixed(2)}s`}
                        </td>
                        <td>
                          <div className="tools-tags">
                            {[
                              ...pageIssues(p),
                              ...(duplicates.has(p.url)
                                ? ["Duplicate metadata"]
                                : []),
                            ].map((issue) => (
                              <span key={issue} className="tools-tag">
                                {issue}
                              </span>
                            ))}
                            {pageIssues(p).length === 0 &&
                              !duplicates.has(p.url) && (
                                <span className="tools-tag tools-tag-clear">
                                  No flags in these checks
                                </span>
                              )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <Empty
                title={
                  result.pages_crawled
                    ? "No matching pages"
                    : "No pages could be fetched"
                }
              >
                {result.pages_crawled
                  ? "Try another filter or search."
                  : "The page may be unavailable or disallowed by robots.txt. Check the URL or try a different starting page."}
              </Empty>
            )}
          </section>
          {(Object.keys(result.duplicate_titles).length > 0 ||
            Object.keys(result.duplicate_meta_descriptions).length > 0) && (
            <section className="panel">
              <h2 className="panel-title">Duplicate metadata groups</h2>
              {[
                ["Title", result.duplicate_titles],
                ["Description", result.duplicate_meta_descriptions],
              ].map(([label, groups]) =>
                Object.entries(groups as Record<string, string[]>).map(
                  ([value, urls]) => (
                    <details
                      className="finding-detail"
                      key={`${label}-${value}`}
                    >
                      <summary>
                        {String(label)}: {value}{" "}
                        <small>{urls.length} pages</small>
                      </summary>
                      <div className="finding-body">
                        {urls.map((u) => (
                          <p key={u} className="break-all">
                            {u}
                          </p>
                        ))}
                      </div>
                    </details>
                  ),
                ),
              )}
            </section>
          )}
          {result.broken_internal_links.length > 0 && (
            <section className="panel">
              <h2 className="panel-title">Failed URLs encountered</h2>
              <p className="panel-subtitle">
                These requests failed during this crawl. Check whether each URL
                is still needed.
              </p>
              {result.broken_internal_links.map((u) => (
                <p key={u} className="text-xs break-all">
                  {u}
                </p>
              ))}
            </section>
          )}
        </>
      )}
    </div>
  );
}
