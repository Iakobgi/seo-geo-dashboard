import React, { useState } from 'react'
import { Loader2, Sparkles } from 'lucide-react'
import { agentApi, type AgentResult } from '../api/endpoints'

const AgentPanel: React.FC = () => {
  const [url, setUrl] = useState('')
  const [targetScore, setTargetScore] = useState(90)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AgentResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const runAgent = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!url.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await agentApi.run(url.trim(), targetScore)
      setResult(res.data)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Agent run failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="text-purple-600" size={20} />
        <h2 className="text-lg font-semibold">AI Agent — Auto-Optimize</h2>
      </div>
      <p className="text-sm text-gray-500 mb-4">
        Give the agent a URL and a target SEO score. It audits the page, then generates a prioritized
        action plan and rewritten on-page content (title, meta, H1, FAQ, JSON-LD schema).
      </p>
      <form onSubmit={runAgent} className="flex flex-col sm:flex-row gap-2 mb-4">
        <input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://yourwebsite.com"
          className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
        />
        <input
          type="number"
          min={0}
          max={100}
          value={targetScore}
          onChange={(e) => setTargetScore(Number(e.target.value))}
          className="w-full sm:w-28 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
        />
        <button
          disabled={loading}
          className="flex items-center justify-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-purple-700 disabled:opacity-50"
        >
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
          Optimize automatically
        </button>
      </form>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {result && (
        <div className="mt-4 border-t border-gray-100 pt-4 space-y-4">
          <div className="flex gap-6 text-sm">
            <div>
              Status: <span className="font-semibold">{result.status.replace('_', ' ')}</span>
            </div>
            <div>
              SEO: <span className="font-semibold text-blue-600">{result.current_seo_score}</span>
            </div>
            <div>
              GEO: <span className="font-semibold text-emerald-600">{result.current_geo_score}</span>
            </div>
          </div>

          {result.actions.length > 0 && (
            <div>
              <h3 className="font-medium text-sm mb-2">Action plan</h3>
              <ul className="list-disc list-inside text-sm space-y-1 text-gray-700">
                {result.actions.map((a, i) => (
                  <li key={i}>{a}</li>
                ))}
              </ul>
            </div>
          )}

          {result.generated_content && (
            <div>
              <h3 className="font-medium text-sm mb-2">Generated content</h3>
              <pre className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-xs overflow-x-auto">
                {JSON.stringify(result.generated_content, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default AgentPanel
