import { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Search, Tags, ListChecks, Globe2, ArrowUpRight } from "lucide-react";
import {
  auditsApi,
  keywordsApi,
  type Audit,
  type Keyword,
} from "../api/endpoints";
import { errorMessage } from "../api/helpers";
import SEOScoreCard from "../components/SEOScoreCard";
import RecommendationList from "../components/RecommendationList";
import KeywordTracker from "../components/KeywordTracker";
import AuditForm from "../components/AuditForm";
import { Loading, Notice, Empty, PageHeading } from "../components/UI";
export default function Dashboard() {
  const [audits, setAudits] = useState<Audit[]>([]);
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [url, setUrl] = useState("");
  const refresh = useCallback(async () => {
    setError(null);
    const results = await Promise.allSettled([
      auditsApi.list(),
      keywordsApi.list(),
    ]);
    if (results[0].status === "fulfilled") setAudits(results[0].value.data);
    if (results[1].status === "fulfilled") setKeywords(results[1].value.data);
    const failed = results.find((result) => result.status === "rejected");
    if (failed?.status === "rejected")
      setError(
        errorMessage(failed.reason, "Some workspace data could not be loaded."),
      );
    setLoading(false);
  }, []);
  useEffect(() => {
    void refresh();
  }, [refresh]);
  if (loading) return <Loading />;
  const latest = audits[0];
  const urls = [...new Set(audits.map((a) => a.url))];
  const chartUrl = urls.includes(url) ? url : latest?.url;
  const history = audits
    .filter((a) => a.url === chartUrl)
    .slice()
    .reverse()
    .map((a) => ({
      date: new Date(a.created_at).toLocaleString(),
      seo: a.seo_score,
      geo: a.geo_score,
    }));
  const pending = audits
    .flatMap((a) => a.recommendations)
    .filter((r) => r.type === "suggestion" && r.status === "pending").length;
  const stats = [
    {
      label: "Audits completed",
      value: audits.length,
      note: "Your full audit history",
      icon: Search,
    },
    {
      label: "Pages analyzed",
      value: urls.length,
      note: "Unique website URLs",
      icon: Globe2,
    },
    {
      label: "Keywords tracked",
      value: keywords.length,
      note: "In your keyword watchlist",
      icon: Tags,
    },
    {
      label: "Open recommendations",
      value: pending,
      note: "Pending page improvements",
      icon: ListChecks,
    },
  ];
  return (
    <div className="space-y-6">
      <PageHeading
        title="Workspace overview"
        description="Review your audit scores, keyword watchlist, and page recommendations."
        action={
          <Link to="/audits" className="button button-secondary">
            View all audits <ArrowUpRight size={15} />
          </Link>
        }
      />
      {error && <Notice retry={refresh}>{error}</Notice>}
      <div className="stat-grid">
        {stats.map(({ label, value, note, icon: Icon }) => (
          <div key={label} className="stat-card">
            <div>
              {label}
              <Icon size={16} />
            </div>
            <strong>{value}</strong>
            <p>{note}</p>
          </div>
        ))}
      </div>
      <AuditForm onCreated={refresh} />
      <div className="dashboard-grid">
        <SEOScoreCard audit={latest} />
        <div className="panel">
          <div className="table-toolbar">
            <div>
              <h2 className="panel-title">Progress over time</h2>
              <p className="panel-subtitle mb-0">
                Compare audits of the same page.
              </p>
            </div>
            {urls.length > 0 && (
              <select
                className="search-input max-w-full"
                style={{ minWidth: 0, width: 180 }}
                aria-label="Page for score history"
                value={chartUrl}
                onChange={(e) => setUrl(e.target.value)}
              >
                {urls.map((value) => (
                  <option key={value}>{value}</option>
                ))}
              </select>
            )}
          </div>
          {history.length === 0 ? (
            <Empty title="No audit history yet">
              Run an audit to begin. Re-audit the same page after making
              improvements.
            </Empty>
          ) : (
            <>
              <ResponsiveContainer width="100%" height={230}>
                <LineChart
                  data={history}
                  margin={{ top: 12, right: 10, left: -25, bottom: 0 }}
                >
                  <CartesianGrid
                    strokeDasharray="3 5"
                    vertical={false}
                    stroke="#e6edf7"
                  />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 9, fill: "#8293ac" }}
                    tickFormatter={(value) => value.split(",")[0]}
                    axisLine={false}
                    tickLine={false}
                    minTickGap={30}
                  />
                  <YAxis
                    domain={[0, 100]}
                    tick={{ fontSize: 10, fill: "#8293ac" }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip
                    contentStyle={{
                      borderRadius: 10,
                      border: "1px solid #e2e8eb",
                      fontSize: 12,
                    }}
                  />
                  <Legend
                    iconType="circle"
                    wrapperStyle={{ fontSize: 11, paddingTop: 15 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="seo"
                    stroke="#397ee2"
                    strokeWidth={2.5}
                    name="SEO"
                    dot={{ r: 4 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="geo"
                    stroke="#38a5dd"
                    strokeWidth={2.5}
                    name="GEO"
                    dot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
              {history.length === 1 && (
                <p className="panel-subtitle mt-3 mb-0">
                  Re-audit this page to see how your scores change.
                </p>
              )}
            </>
          )}
        </div>
      </div>
      <div className="dashboard-grid">
        <RecommendationList
          recommendations={latest?.recommendations ?? []}
          onChanged={refresh}
        />
        <KeywordTracker keywords={keywords} onChanged={refresh} />
      </div>
    </div>
  );
}
