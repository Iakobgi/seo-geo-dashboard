import React, { useEffect, useState, useCallback } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { auditsApi, keywordsApi, type Audit, type Keyword } from '../api/endpoints'
import SEOScoreCard from '../components/SEOScoreCard'
import RecommendationList from '../components/RecommendationList'
import KeywordTracker from '../components/KeywordTracker'
import AuditForm from '../components/AuditForm'

const Dashboard: React.FC = () => {
  const [audits, setAudits] = useState<Audit[]>([])
  const [keywords, setKeywords] = useState<Keyword[]>([])
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    const [auditsRes, keywordsRes] = await Promise.all([auditsApi.list(), keywordsApi.list()])
    setAudits(auditsRes.data)
    setKeywords(keywordsRes.data)
    setLoading(false)
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  if (loading) return <div className="p-6">Loading...</div>

  const latest = audits[0]
  const history = [...audits]
    .reverse()
    .map((a) => ({ date: new Date(a.created_at).toLocaleDateString(), seo: a.seo_score, geo: a.geo_score }))

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>

      <AuditForm onCreated={refresh} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SEOScoreCard audit={latest} />
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold mb-3">Score history</h2>
          {history.length === 0 ? (
            <p className="text-sm text-gray-500">No audits yet.</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={history}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" fontSize={12} />
                <YAxis domain={[0, 100]} fontSize={12} />
                <Tooltip />
                <Line type="monotone" dataKey="seo" stroke="#3b82f6" name="SEO" />
                <Line type="monotone" dataKey="geo" stroke="#10b981" name="GEO" />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecommendationList recommendations={latest?.recommendations ?? []} onChanged={refresh} />
        <KeywordTracker keywords={keywords} onChanged={refresh} />
      </div>
    </div>
  )
}

export default Dashboard
