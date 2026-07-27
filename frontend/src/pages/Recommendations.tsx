import React, { useEffect, useState, useCallback } from 'react'
import { auditsApi, type Audit } from '../api/endpoints'
import RecommendationList from '../components/RecommendationList'

const Recommendations: React.FC = () => {
  const [audits, setAudits] = useState<Audit[]>([])
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    const res = await auditsApi.list()
    setAudits(res.data)
    setLoading(false)
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  if (loading) return <div className="p-6">Loading...</div>

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-slate-800">Recommendations</h1>
      {audits.length === 0 && <p className="text-sm text-gray-500">Run an audit first to get recommendations.</p>}
      {audits.map((audit) => (
        <div key={audit.id}>
          <p className="text-sm text-gray-500 mb-2 truncate">{audit.url}</p>
          <RecommendationList recommendations={audit.recommendations} onChanged={refresh} />
        </div>
      ))}
    </div>
  )
}

export default Recommendations
