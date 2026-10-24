import { useEffect, useState, useCallback } from "react";
import { Trash2, Mail, Download, X } from "lucide-react";
import { auditsApi, reportsApi, type Audit } from "../api/endpoints";
import { downloadFile, errorMessage } from "../api/helpers";
import AuditForm from "../components/AuditForm";
import RecommendationList from "../components/RecommendationList";
import SEOScoreCard from "../components/SEOScoreCard";
import AuditFindings from "../components/AuditFindings";
import { Loading, Notice, Empty, PageHeading } from "../components/UI";
export default function Audits() {
  const [audits, setAudits] = useState<Audit[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [deleting, setDeleting] = useState<number | null>(null);
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState("newest");
  const refresh = useCallback(async () => {
    setError(null);
    try {
      setAudits((await auditsApi.list()).data);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    void refresh();
  }, [refresh]);
  const remove = async (id: number) => {
    setBusy(true);
    setError(null);
    try {
      await auditsApi.remove(id);
      if (selected === id) setSelected(null);
      setDeleting(null);
      await refresh();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };
  const emailReport = async (id: number) => {
    setBusy(true);
    setError(null);
    setMessage("");
    try {
      const res = await reportsApi.emailAudit(id);
      setMessage(
        res.data.emailed
          ? "Report sent to your account email."
          : "The report could not be sent. Email delivery needs to be configured or restored. You can download the report instead.",
      );
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };
  const filtered = audits
    .filter((a) =>
      `${a.url} ${a.title || ""}`.toLowerCase().includes(query.toLowerCase()),
    )
    .sort((a, b) =>
      sort === "seo"
        ? b.seo_score - a.seo_score
        : sort === "geo"
          ? b.geo_score - a.geo_score
          : new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
    );
  const selectedAudit = audits.find((a) => a.id === selected);
  if (loading) return <Loading />;
  return (
    <div className="space-y-6">
      <PageHeading
        title="Website audits"
        description="Explore page insights, compare scores, and keep your next steps organized."
      />
      {error && <Notice retry={refresh}>{error}</Notice>}
      {message && (
        <div role="status" className="success-message">
          {message}
        </div>
      )}
      <AuditForm onCreated={refresh} />
      <section className="panel">
        <div className="table-toolbar">
          <div>
            <h2 className="panel-title">
              Audit library{" "}
              <span className="text-gray-400 font-normal">
                ({audits.length})
              </span>
            </h2>
            <p className="panel-subtitle mb-0">
              Select a page to explore its details.
            </p>
          </div>
          <div className="flex gap-2 flex-wrap">
            <input
              aria-label="Search audits"
              className="search-input"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search URL or page title…"
            />
            <select
              aria-label="Sort audits"
              className="search-input"
              style={{ minWidth: 130 }}
              value={sort}
              onChange={(e) => setSort(e.target.value)}
            >
              <option value="newest">Newest first</option>
              <option value="seo">Highest SEO</option>
              <option value="geo">Highest GEO</option>
            </select>
          </div>
        </div>
        {deleting !== null && (
          <div className="notice">
            <span>
              Delete this audit and its recommendations? This cannot be undone.
            </span>
            <button disabled={busy} onClick={() => remove(deleting)}>
              Delete
            </button>
            <button disabled={busy} onClick={() => setDeleting(null)}>
              Cancel
            </button>
          </div>
        )}
        {filtered.length === 0 ? (
          <Empty
            title={query ? "No matching pages" : "Start with your first page"}
          >
            {query
              ? "Try a different URL or page title."
              : "Run an audit above to build your visibility library."}
          </Empty>
        ) : (
          <div className="table-scroll">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Page</th>
                  <th>SEO score</th>
                  <th>GEO score</th>
                  <th>Audited</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((a) => (
                  <tr key={a.id}>
                    <td>
                      <button
                        className="url-button"
                        title={a.url}
                        onClick={() => setSelected(a.id)}
                      >
                        {a.title || a.url}
                      </button>
                      <span className="block text-gray-400 text-[10px] max-w-[290px] truncate">
                        {a.url}
                      </span>
                    </td>
                    <td>
                      <span className="score-badge seo">{a.seo_score}</span>
                    </td>
                    <td>
                      <span className="score-badge">{a.geo_score}</span>
                    </td>
                    <td className="text-gray-400">
                      {new Date(a.created_at).toLocaleDateString()}
                    </td>
                    <td>
                      <div className="flex gap-1">
                        <button
                          className="icon-button"
                          disabled={busy}
                          onClick={() => emailReport(a.id)}
                          title="Email report"
                          aria-label={`Email report for ${a.url}`}
                        >
                          <Mail size={15} />
                        </button>
                        <button
                          className="icon-button"
                          onClick={() =>
                            downloadFile(
                              `audit-${a.id}.json`,
                              JSON.stringify(a, null, 2),
                            )
                          }
                          title="Download report"
                          aria-label={`Download report for ${a.url}`}
                        >
                          <Download size={15} />
                        </button>
                        <button
                          className="icon-button"
                          disabled={busy}
                          onClick={() => setDeleting(a.id)}
                          title="Delete audit"
                          aria-label={`Delete audit for ${a.url}`}
                        >
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
      {selectedAudit && (
        <section aria-label="Selected audit details" className="space-y-5">
          <div className="flex justify-between items-center">
            <h2 className="panel-title mb-0">Page details</h2>
            <button
              onClick={() => setSelected(null)}
              className="icon-button"
              aria-label="Close page details"
            >
              <X size={18} />
            </button>
          </div>
          <div className="dashboard-grid">
            <SEOScoreCard audit={selectedAudit} />
            <div className="panel detail-grid">
              <div>
                <small>WORDS</small>
                {selectedAudit.word_count}
              </div>
              <div>
                <small>IMAGES</small>
                {selectedAudit.images_count}
              </div>
              <div>
                <small>LINKS</small>
                {selectedAudit.links_count}
              </div>
              <div className="wide">
                <small>PAGE TITLE</small>
                {selectedAudit.title || "No title found"}
              </div>
              <div className="wide">
                <small>META DESCRIPTION</small>
                {selectedAudit.meta_description || "No meta description found"}
              </div>
              <div className="wide">
                <small>MAIN HEADING</small>
                {selectedAudit.h1 || "No H1 found"}
              </div>
            </div>
          </div>
          <AuditFindings key={selectedAudit.id} auditId={selectedAudit.id} />
          <RecommendationList
            recommendations={selectedAudit.recommendations}
            onChanged={refresh}
          />
        </section>
      )}
    </div>
  );
}
