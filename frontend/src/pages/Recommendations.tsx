import { useCallback, useEffect, useState } from "react";
import { auditsApi, type Audit } from "../api/endpoints";
import { errorMessage } from "../api/helpers";
import RecommendationList from "../components/RecommendationList";
import { PageHeading, Notice, Loading, Empty } from "../components/UI";
export default function Recommendations() {
  const [audits, setAudits] = useState<Audit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
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
  if (loading) return <Loading />;
  return (
    <div className="space-y-6">
      <PageHeading
        title="Turn insight into improvement."
        description="Work through your page recommendations and keep track of what you’ve applied."
      />
      {error && <Notice retry={refresh}>{error}</Notice>}
      {audits.length === 0 && (
        <div className="panel">
          <Empty title="Your next steps will appear here">
            Run a website audit to generate recommendations for your page.
          </Empty>
        </div>
      )}
      {audits.map((audit) => (
        <section key={audit.id}>
          <p className="text-xs text-gray-500 mb-2 break-all">
            {audit.url} · {new Date(audit.created_at).toLocaleDateString()}
          </p>
          <RecommendationList
            recommendations={audit.recommendations}
            onChanged={refresh}
          />
        </section>
      ))}
    </div>
  );
}
