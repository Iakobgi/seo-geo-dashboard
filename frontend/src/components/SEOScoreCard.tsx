import type { Audit } from "../api/endpoints";
import { Empty } from "./UI";
function Ring({
  value,
  label,
  color,
}: {
  value: number;
  label: string;
  color: string;
}) {
  const score = Math.max(0, Math.min(100, value));
  return (
    <div>
      <div
        className="score-ring"
        role="img"
        aria-label={`${label}: ${score} out of 100`}
      >
        <svg viewBox="0 0 120 120" aria-hidden="true">
          <circle
            cx="60"
            cy="60"
            r="51"
            fill="none"
            stroke="#edf1f2"
            strokeWidth="7"
          />
          <circle
            cx="60"
            cy="60"
            r="51"
            fill="none"
            stroke={color}
            strokeWidth="7"
            strokeLinecap="round"
            strokeDasharray={`${(score / 100) * 320.44} 320.44`}
          />
        </svg>
        <div>
          <strong>{Number(score.toFixed(1))}</strong>
          <small>out of 100</small>
        </div>
      </div>
      <p className="score-caption">{label}</p>
    </div>
  );
}
export default function SEOScoreCard({ audit }: { audit?: Audit }) {
  return (
    <div className="panel">
      <h2 className="panel-title">Latest page snapshot</h2>
      {audit ? (
        <>
          <p className="score-url" title={audit.url}>
            {audit.url}
          </p>
          <div className="score-pair">
            <Ring value={audit.seo_score} label="SEO score" color="#4f719b" />
            <Ring value={audit.geo_score} label="GEO score" color="#4a9b80" />
          </div>
          <div className="score-footer">
            <span>{audit.word_count.toLocaleString()} words analyzed</span>
            <span>{new Date(audit.created_at).toLocaleDateString()}</span>
          </div>
        </>
      ) : (
        <Empty title="Your first insight is one audit away">
          Enter a website URL above to see its search and AI readiness scores.
        </Empty>
      )}
    </div>
  );
}
