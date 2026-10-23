import { useEffect, useState } from "react";
import { auditsApi, type Finding } from "../api/endpoints";
import { errorMessage } from "../api/helpers";
import { Empty, Loading, Notice } from "./UI";

export default function AuditFindings({ auditId }: { auditId: number }) {
  const [findings, setFindings] = useState<Finding[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [severity, setSeverity] = useState("all");
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    auditsApi
      .findings(auditId)
      .then((res) => {
        if (active) setFindings(res.data);
      })
      .catch((err) => {
        if (active) setError(errorMessage(err));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [auditId, retry]);
  const order = ["critical", "high", "medium", "low", "pass"];
  const filtered = findings
    .filter((f) => severity === "all" || f.severity === severity)
    .sort((a, b) => order.indexOf(a.severity) - order.indexOf(b.severity));
  return (
    <div className="panel">
      <div className="table-toolbar">
        <div>
          <h2 className="panel-title">Findings & evidence</h2>
          <p className="panel-subtitle mb-0">
            Open a finding to see what was detected and how to improve it.
          </p>
        </div>
        <select
          className="search-input"
          aria-label="Filter findings by severity"
          style={{ minWidth: 140 }}
          value={severity}
          onChange={(e) => setSeverity(e.target.value)}
        >
          <option value="all">All severities</option>
          {order.map((value) => (
            <option key={value} value={value}>
              {value.charAt(0).toUpperCase() + value.slice(1)}
            </option>
          ))}
        </select>
      </div>
      {loading ? (
        <Loading />
      ) : error ? (
        <Notice retry={() => setRetry((value) => value + 1)}>{error}</Notice>
      ) : filtered.length === 0 ? (
        <Empty title="No findings in this view">
          Older audits may not include structured findings. Run another audit to
          collect them.
        </Empty>
      ) : (
        <div className="space-y-2">
          {filtered.map((f) => (
            <details key={f.id} className="finding-detail">
              <summary>
                <span className={`finding-severity severity-${f.severity}`}>
                  {f.severity}
                </span>
                <span>{f.title}</span>
                <small>{f.category.replace(/_/g, " ")}</small>
              </summary>
              <div className="finding-body">
                <p>{f.description}</p>
                <p>
                  <strong>Next step:</strong> {f.recommendation}
                </p>
                {f.evidence && (
                  <details>
                    <summary>View evidence</summary>
                    <pre>{JSON.stringify(f.evidence, null, 2)}</pre>
                  </details>
                )}
              </div>
            </details>
          ))}
        </div>
      )}
    </div>
  );
}
