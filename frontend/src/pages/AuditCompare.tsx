import { useEffect, useState } from "react";
import { ArrowRightLeft } from "lucide-react";
import {
  auditsApi,
  comparisonApi,
  type Audit,
  type AuditComparison,
  type Finding,
} from "../api/endpoints";
import { errorMessage } from "../api/helpers";
import { Empty, Loading, Notice, PageHeading } from "../components/UI";
import { Link } from "react-router-dom";
function signed(value: number) {
  return `${value > 0 ? "+" : ""}${value.toFixed(1)}`;
}
export default function AuditCompare() {
  const [audits, setAudits] = useState<Audit[]>([]);
  const [baseline, setBaseline] = useState(0);
  const [comparison, setComparison] = useState(0);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retry, setRetry] = useState(0);
  const [data, setData] = useState<AuditComparison | null>(null);
  const [findings, setFindings] = useState<[Finding[], Finding[]] | null>(null);
  const [findingError, setFindingError] = useState(false);
  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    auditsApi
      .list()
      .then(({ data }) => {
        if (active) {
          setAudits(data);
          setBaseline(data[1]?.id || 0);
          setComparison(data[0]?.id || 0);
        }
      })
      .catch((e) => {
        if (active) setError(errorMessage(e));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [retry]);
  useEffect(() => {
    setData(null);
    setFindings(null);
    setFindingError(false);
    if (!baseline || !comparison || baseline === comparison) return;
    let active = true;
    setBusy(true);
    setError(null);
    Promise.allSettled([
      comparisonApi.get(baseline, comparison),
      auditsApi.findings(baseline),
      auditsApi.findings(comparison),
    ])
      .then((results) => {
        if (!active) return;
        const [scores, left, right] = results;
        if (scores.status === "fulfilled") setData(scores.value.data);
        else setError(errorMessage(scores.reason));
        if (left.status === "fulfilled" && right.status === "fulfilled")
          setFindings([left.value.data, right.value.data]);
        else setFindingError(true);
      })
      .finally(() => {
        if (active) setBusy(false);
      });
    return () => {
      active = false;
    };
  }, [baseline, comparison, retry]);
  const a = audits.find((v) => v.id === baseline),
    b = audits.find((v) => v.id === comparison);
  const signature = (f: Finding) => `${f.category}|${f.title}|${f.url || ""}`;
  const leftSet = new Set(findings?.[0].map(signature));
  const rightSet = new Set(findings?.[1].map(signature));
  const uniqueLeft =
    findings?.[0].filter(
      (f) => f.severity !== "pass" && !rightSet.has(signature(f)),
    ) || [];
  const uniqueRight =
    findings?.[1].filter(
      (f) => f.severity !== "pass" && !leftSet.has(signature(f)),
    ) || [];
  return (
    <div className="space-y-6">
      <PageHeading
        title="Compare audits"
        description="Compare saved snapshots to review score changes, page metadata, and differences in detected findings."
      />
      {error && <Notice retry={() => setRetry((v) => v + 1)}>{error}</Notice>}
      {loading ? (
        <Loading />
      ) : audits.length < 2 ? (
        <div className="panel">
          <Empty title="Two audits are needed">
            Run another audit of your page, then compare the results here.{" "}
            <Link className="text-blue-600" to="/audits">
              Open website audits
            </Link>
            .
          </Empty>
        </div>
      ) : (
        <>
          <section className="panel compare-selectors">
            <label className="field">
              Baseline
              <select
                className="search-input"
                aria-label="Baseline audit"
                value={baseline}
                onChange={(e) => setBaseline(Number(e.target.value))}
              >
                {audits.map((a) => (
                  <option value={a.id} key={a.id}>
                    {a.url} - {new Date(a.created_at).toLocaleString()} (#{a.id}
                    )
                  </option>
                ))}
              </select>
            </label>
            <button
              className="icon-button"
              aria-label="Swap audits"
              onClick={() => {
                setBaseline(comparison);
                setComparison(baseline);
              }}
            >
              <ArrowRightLeft size={20} />
            </button>
            <label className="field">
              Comparison
              <select
                className="search-input"
                aria-label="Comparison audit"
                value={comparison}
                onChange={(e) => setComparison(Number(e.target.value))}
              >
                {audits.map((a) => (
                  <option value={a.id} key={a.id}>
                    {a.url} - {new Date(a.created_at).toLocaleString()} (#{a.id}
                    )
                  </option>
                ))}
              </select>
            </label>
          </section>
          {baseline === comparison ? (
            <div className="panel">
              <Empty title="Select two different audits">
                Choose another snapshot in either menu.
              </Empty>
            </div>
          ) : busy ? (
            <Loading />
          ) : (
            a &&
            b &&
            data && (
              <>
                <p className="tools-help">
                  {a.url === b.url
                    ? "Comparing two snapshots of the same page. Positive score changes indicate higher audit scores."
                    : "Different URLs selected: this is a page comparison, not a before-and-after measurement."}{" "}
                  Audit scores are page checks, not search rankings.
                </p>
                <div className="tools-two-column">
                  {[
                    [
                      "SEO score",
                      data.seo_score_change,
                      a.seo_score,
                      b.seo_score,
                    ],
                    [
                      "GEO score",
                      data.geo_score_change,
                      a.geo_score,
                      b.geo_score,
                    ],
                  ].map(([label, delta, start, end]) => (
                    <section key={label} className="panel compare-score">
                      <h2 className="panel-title">{label}</h2>
                      <strong>
                        {Number(start).toFixed(1)} <span>to</span>{" "}
                        {Number(end).toFixed(1)}
                      </strong>
                      <p className="score-badge">
                        {signed(Number(delta))} points
                      </p>
                    </section>
                  ))}
                </div>
                <section className="panel">
                  <h2 className="panel-title">Page details</h2>
                  <div className="table-scroll">
                    <table className="data-table compare-table">
                      <thead>
                        <tr>
                          <th>Metric</th>
                          <th>Baseline</th>
                          <th>Comparison</th>
                        </tr>
                      </thead>
                      <tbody>
                        {[
                          ["Title", a.title, b.title],
                          [
                            "Description",
                            a.meta_description,
                            b.meta_description,
                          ],
                          ["H1", a.h1, b.h1],
                          ["Words", a.word_count, b.word_count],
                          ["Images", a.images_count, b.images_count],
                          ["Links", a.links_count, b.links_count],
                          [
                            "Response time",
                            a.load_time === null
                              ? "Unavailable"
                              : `${a.load_time.toFixed(2)}s`,
                            b.load_time === null
                              ? "Unavailable"
                              : `${b.load_time.toFixed(2)}s`,
                          ],
                        ].map(([label, left, right]) => (
                          <tr key={label}>
                            <th>{label}</th>
                            <td>{left ?? "Not found"}</td>
                            <td
                              className={
                                left !== right ? "compare-changed" : ""
                              }
                            >
                              {right ?? "Not found"}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </section>
                {findingError ? (
                  <Notice>
                    Finding details could not be loaded. Re-select an audit to
                    try again. Scores above are still available.
                  </Notice>
                ) : (
                  findings && (
                    <div className="tools-two-column">
                      {[
                        ["Only in baseline", uniqueLeft],
                        ["Only in comparison", uniqueRight],
                      ].map(([label, items]) => (
                        <section className="panel" key={String(label)}>
                          <h2 className="panel-title">
                            {String(label)} ({(items as Finding[]).length})
                          </h2>
                          <p className="panel-subtitle">
                            Differences in detected findings, not verified
                            fixes. Older audits may lack structured findings.
                          </p>
                          {(items as Finding[]).length ? (
                            (items as Finding[]).map((f) => (
                              <details className="finding-detail" key={f.id}>
                                <summary>
                                  <span
                                    className={`finding-severity severity-${f.severity}`}
                                  >
                                    {f.severity}
                                  </span>
                                  {f.title}
                                </summary>
                                <div className="finding-body">
                                  <p>{f.description}</p>
                                  <p>{f.recommendation}</p>
                                </div>
                              </details>
                            ))
                          ) : (
                            <p className="tools-help">
                              No unique findings in this snapshot.
                            </p>
                          )}
                        </section>
                      ))}
                    </div>
                  )
                )}
              </>
            )
          )}
        </>
      )}
    </div>
  );
}
