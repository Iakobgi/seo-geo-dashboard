import { useEffect, useState } from "react";
import { ArrowDown, ArrowUp, Minus, RefreshCw, Trash2 } from "lucide-react";
import { keywordsApi, type Keyword } from "../api/endpoints";
import { errorMessage } from "../api/helpers";
import { Empty, Notice } from "./UI";
export default function KeywordTracker({
  keywords,
  onChanged,
}: {
  keywords: Keyword[];
  onChanged: () => void;
}) {
  const [keyword, setKeyword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [simulated, setSimulated] = useState<boolean | null>(null);
  useEffect(() => {
    let active = true;
    keywordsApi
      .provider()
      .then((res) => {
        if (active) setSimulated(res.data.simulated);
      })
      .catch(() => {});
    return () => {
      active = false;
    };
  }, []);
  const act = async (operation: () => Promise<unknown>) => {
    setBusy(true);
    setError(null);
    try {
      await operation();
      onChanged();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };
  const add = async (e: React.FormEvent) => {
    e.preventDefault();
    const value = keyword.trim();
    if (!value) return;
    if (keywords.some((k) => k.keyword.toLowerCase() === value.toLowerCase())) {
      setError("You’re already tracking this keyword.");
      return;
    }
    await act(async () => {
      await keywordsApi.create(value);
      setKeyword("");
    });
  };
  return (
    <div className="panel">
      <h2 className="panel-title">
        Keyword watchlist{" "}
        {simulated && <span className="score-badge ml-2">Demo data</span>}
      </h2>
      <p className="panel-subtitle">Keep your target search terms in view.</p>
      <form onSubmit={add} className="flex gap-2 mb-4">
        <input
          required
          maxLength={200}
          aria-label="New keyword"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          placeholder="Add a keyword…"
          className="search-input flex-1"
          style={{ minWidth: 0 }}
        />
        <button
          disabled={busy || !keyword.trim()}
          className="button button-dark"
        >
          Add
        </button>
      </form>
      {error && <Notice>{error}</Notice>}
      {keywords.length > 5 && (
        <input
          aria-label="Search keywords"
          className="search-input w-full mb-3"
          placeholder="Filter keywords…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      )}
      <div className="max-h-72 overflow-auto">
        {keywords.length === 0 && (
          <Empty title="What do you want to be found for?">
            Add your first keyword to start building a watchlist.
          </Empty>
        )}
        {keywords.length > 0 &&
          !keywords.some((k) =>
            k.keyword.toLowerCase().includes(query.toLowerCase()),
          ) && <p className="panel-subtitle">No matching keywords.</p>}
        {keywords
          .filter((k) => k.keyword.toLowerCase().includes(query.toLowerCase()))
          .map((k) => (
            <div
              key={k.id}
              className="flex items-center justify-between border-b border-gray-100 py-3 gap-3 text-xs"
            >
              <div className="flex items-center gap-2 min-w-0">
                {k.previous_position == null ||
                k.position == null ||
                k.position === k.previous_position ? (
                  <Minus size={13} className="shrink-0 text-gray-400" />
                ) : k.position < k.previous_position ? (
                  <ArrowUp size={13} className="shrink-0 text-emerald-600" />
                ) : (
                  <ArrowDown size={13} className="shrink-0 text-red-500" />
                )}
                <span className="break-words">{k.keyword}</span>
              </div>
              <div className="flex items-center shrink-0 gap-2">
                <span className="text-gray-400 text-[10px]">
                  #{k.position ?? "—"} · Vol.{" "}
                  {k.volume?.toLocaleString() ?? "—"}
                </span>
                <button
                  disabled={busy}
                  onClick={() => act(() => keywordsApi.refresh(k.id))}
                  className="icon-button"
                  title="Refresh position"
                  aria-label={`Refresh ${k.keyword}`}
                >
                  <RefreshCw size={13} />
                </button>
                <button
                  disabled={busy}
                  onClick={() => act(() => keywordsApi.remove(k.id))}
                  className="icon-button text-gray-400"
                  title="Remove keyword"
                  aria-label={`Remove ${k.keyword}`}
                >
                  <Trash2 size={13} />
                </button>
              </div>
            </div>
          ))}
      </div>
    </div>
  );
}
