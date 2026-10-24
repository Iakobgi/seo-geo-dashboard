import { useState } from "react";
import { Loader2, ArrowUpRight } from "lucide-react";
import { auditsApi } from "../api/endpoints";
import { normalizeUrl, errorMessage } from "../api/helpers";
import { Notice } from "./UI";
export default function AuditForm({ onCreated }: { onCreated: () => void }) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    let normalized: string;
    try {
      normalized = normalizeUrl(url);
    } catch {
      setError(
        "Enter a valid website, such as example.com or https://example.com.",
      );
      return;
    }
    setLoading(true);
    try {
      await auditsApi.create(normalized);
      setUrl("");
      onCreated();
    } catch (err) {
      setError(
        errorMessage(err, "Unable to audit this page. Please try another URL."),
      );
    } finally {
      setLoading(false);
    }
  };
  return (
    <form onSubmit={submit} className="panel audit-form">
      <div>
        <h2 className="panel-title">Analyze a website page</h2>
        <p>Analyze a page for search and AI readiness.</p>
      </div>
      <div className="audit-input-row">
        <label htmlFor="audit-url" className="sr-only">
          Website URL
        </label>
        <input
          id="audit-url"
          required
          disabled={loading}
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter your website URL"
          autoComplete="url"
        />
        <button disabled={loading} className="button button-dark">
          {loading ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <ArrowUpRight size={16} />
          )}
          {loading ? "Analyzing…" : "Run audit"}
        </button>
      </div>
      {loading && (
        <div className="audit-progress" role="status">
          Reading page content and generating recommendations. This may take a
          minute.
        </div>
      )}
      {error && <Notice>{error}</Notice>}
    </form>
  );
}
