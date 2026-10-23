import { useState } from "react";
import { CheckCircle2, XCircle, Circle } from "lucide-react";
import { recommendationsApi, type Recommendation } from "../api/endpoints";
import { errorMessage } from "../api/helpers";
import { Empty, Notice } from "./UI";
export default function RecommendationList({
  recommendations,
  onChanged,
}: {
  recommendations: Recommendation[];
  onChanged?: () => void;
}) {
  const [busy, setBusy] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState("all");
  const suggestions = recommendations.filter((r) => r.type === "suggestion");
  const filtered = suggestions.filter(
    (r) => filter === "all" || r.status === filter,
  );
  const handle = async (id: number, action: "apply" | "dismiss") => {
    setBusy(id);
    setError(null);
    try {
      if (action === "apply") await recommendationsApi.apply(id);
      else await recommendationsApi.dismiss(id);
      onChanged?.();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(null);
    }
  };
  return (
    <div className="panel">
      <div className="table-toolbar">
        <div>
          <h2 className="panel-title">Your next steps</h2>
          <p className="panel-subtitle mb-0">
            Mark improvements as applied after updating your website.
          </p>
        </div>
        <select
          aria-label="Filter recommendations by status"
          className="search-input"
          style={{ minWidth: 100, width: 110 }}
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="all">All statuses</option>
          <option value="pending">Pending</option>
          <option value="applied">Applied</option>
          <option value="dismissed">Dismissed</option>
        </select>
      </div>
      {error && <Notice>{error}</Notice>}
      {filtered.length === 0 && (
        <Empty
          title={
            suggestions.length
              ? "Nothing in this view"
              : "Good decisions start with an audit"
          }
        >
          {suggestions.length
            ? "Choose another status to see more recommendations."
            : "Run a page audit to get recommendations for your content."}
        </Empty>
      )}
      <ul>
        {filtered.map((rec) => (
          <li key={rec.id} className="reco-item">
            <div className="flex gap-3 items-start">
              <Circle
                size={12}
                className={`shrink-0 mt-1 ${rec.status === "applied" ? "text-emerald-600" : "text-gray-400"}`}
              />
              <div>
                <p
                  className={
                    rec.status === "dismissed" ? "line-through opacity-60" : ""
                  }
                >
                  {rec.suggestion}
                </p>
                <small>{rec.status}</small>
              </div>
            </div>
            {rec.status === "pending" && (
              <div className="flex shrink-0">
                <button
                  disabled={busy !== null}
                  className="icon-button text-emerald-600"
                  onClick={() => handle(rec.id, "apply")}
                  title="Mark as applied"
                  aria-label="Mark recommendation as applied"
                >
                  <CheckCircle2 size={17} />
                </button>
                <button
                  disabled={busy !== null}
                  className="icon-button text-gray-400"
                  onClick={() => handle(rec.id, "dismiss")}
                  title="Dismiss"
                  aria-label="Dismiss recommendation"
                >
                  <XCircle size={17} />
                </button>
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
