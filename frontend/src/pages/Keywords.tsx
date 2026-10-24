import { useCallback, useEffect, useState } from "react";
import { keywordsApi, type Keyword } from "../api/endpoints";
import { errorMessage } from "../api/helpers";
import KeywordTracker from "../components/KeywordTracker";
import { PageHeading, Notice, Loading } from "../components/UI";
export default function Keywords() {
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [provider, setProvider] = useState<{
    provider: string;
    simulated: boolean;
  } | null>(null);
  const refresh = useCallback(async () => {
    setError(null);
    try {
      const [list, source] = await Promise.all([
        keywordsApi.list(),
        keywordsApi.provider(),
      ]);
      setKeywords(list.data);
      setProvider(source.data);
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
        title="Keyword tracking"
        description="Build your watchlist and review changes in position and search volume."
      />
      {error && <Notice retry={refresh}>{error}</Notice>}
      <div className="panel text-xs text-gray-500">
        {provider?.simulated
          ? "Demo ranking data: no live search provider is connected. Positions and volumes are simulated and do not represent real search performance."
          : provider
            ? `Search provider: ${provider.provider}.`
            : "Search provider status is unavailable."}
      </div>
      <KeywordTracker keywords={keywords} onChanged={refresh} />
    </div>
  );
}
