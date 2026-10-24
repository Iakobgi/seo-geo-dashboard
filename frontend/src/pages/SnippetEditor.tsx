import { useEffect, useState } from "react";
import { Download, Smartphone, Monitor } from "lucide-react";
import { auditsApi, type Audit } from "../api/endpoints";
import { downloadFile, errorMessage, normalizeUrl } from "../api/helpers";
import { Notice, PageHeading } from "../components/UI";
import { escapeHtml } from "../utils/siteTools";
export default function SnippetEditor() {
  const [audits, setAudits] = useState<Audit[]>([]);
  const [url, setUrl] = useState("https://example.com/your-page");
  const [title, setTitle] = useState("Your page title");
  const [description, setDescription] = useState(
    "Write a concise description of what visitors will find on this page.",
  );
  const [selected, setSelected] = useState("");
  const [mobile, setMobile] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let active = true;
    auditsApi
      .list()
      .then((r) => {
        if (active) setAudits(r.data);
      })
      .catch((e) => {
        if (active)
          setError(
            errorMessage(
              e,
              "Saved audits could not be loaded. You can still edit a snippet manually.",
            ),
          );
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);
  const importAudit = (id: string) => {
    setSelected(id);
    const a = audits.find((a) => a.id === Number(id));
    if (a) {
      setUrl(a.url);
      setTitle(a.title || "");
      setDescription(a.meta_description || "");
      setError(null);
    }
  };
  const exportMetadata = () => {
    try {
      const canonical = normalizeUrl(url);
      downloadFile(
        "page-metadata.html",
        `<title>${escapeHtml(title)}</title>\n<meta name="description" content="${escapeHtml(description)}">\n<link rel="canonical" href="${escapeHtml(canonical)}">\n`,
        "text/html;charset=utf-8",
      );
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Check the URL.");
    }
  };
  let displayUrl = url;
  try {
    displayUrl = new URL(normalizeUrl(url)).hostname;
  } catch {
    /* Keep invalid input as plain preview text. */
  }
  return (
    <div className="space-y-6">
      <PageHeading
        title="Search snippet editor"
        description="Draft page titles and descriptions, preview their appearance, and export the HTML metadata."
      />
      {error && <Notice>{error}</Notice>}
      <div className="tools-two-column snippet-layout">
        <section className="panel">
          <h2 className="panel-title">Page metadata</h2>
          <label className="field">
            Load from saved audit
            <select
              className="search-input"
              aria-label="Load from saved audit"
              value={selected}
              onChange={(e) => importAudit(e.target.value)}
              disabled={loading}
            >
              <option value="">
                {loading
                  ? "Loading audits..."
                  : "Enter manually or select an audit"}
              </option>
              {audits.map((a) => (
                <option value={a.id} key={a.id}>
                  {a.url} (#{a.id})
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            Page URL
            <input
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              inputMode="url"
            />
          </label>
          <label className="field">
            Page title
            <input
              aria-label="Page title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
            <small className="tools-help">
              {title.length} characters. Aim for roughly 50-60; width varies by
              text.
            </small>
          </label>
          <label className="field">
            Meta description
            <textarea
              aria-label="Meta description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={5}
            />
            <small className="tools-help">
              {description.length} characters. A useful starting range is
              140-160.
            </small>
          </label>
          <button
            className="button button-dark"
            onClick={exportMetadata}
            disabled={!title.trim() || !description.trim()}
          >
            <Download size={16} />
            Export HTML
          </button>
          <p className="tools-help mt-4">
            This editor does not change your website or saved audit. Add the
            exported metadata in your website editor.
          </p>
        </section>
        <section className="panel">
          <div className="table-toolbar">
            <h2 className="panel-title">Search preview</h2>
            <div
              className="snippet-device"
              role="group"
              aria-label="Preview device"
            >
              <button
                aria-pressed={!mobile}
                aria-label="Desktop preview"
                onClick={() => setMobile(false)}
              >
                <Monitor size={16} />
              </button>
              <button
                aria-pressed={mobile}
                aria-label="Mobile preview"
                onClick={() => setMobile(true)}
              >
                <Smartphone size={16} />
              </button>
            </div>
          </div>
          <div className={`snippet-preview ${mobile ? "snippet-mobile" : ""}`}>
            <div className="snippet-site">
              <span aria-hidden="true">W</span>
              <div>
                <strong>{displayUrl}</strong>
                <small>{url}</small>
              </div>
            </div>
            <h3>{title || "Your page title"}</h3>
            <p>{description || "Your page description will appear here."}</p>
          </div>
          <p className="tools-help mt-5">
            Illustrative preview. Search engines can rewrite titles and
            descriptions; display length depends on device, font, and query.
          </p>
          <div className="snippet-checks">
            <h3>Editing checklist</h3>
            <ul>
              <li>Describe this specific page and its main topic.</li>
              <li>Keep titles and descriptions unique across pages.</li>
              <li>Use a clear description rather than repeated keywords.</li>
              <li>Check the preview for truncated text on both devices.</li>
            </ul>
          </div>
        </section>
      </div>
    </div>
  );
}
