import React, { useEffect, useState, useCallback } from 'react'
import { keywordsApi, type Keyword } from '../api/endpoints'
import KeywordTracker from '../components/KeywordTracker'

const Keywords: React.FC = () => {
  const [keywords, setKeywords] = useState<Keyword[]>([])
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    const res = await keywordsApi.list()
    setKeywords(res.data)
    setLoading(false)
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  if (loading) return <div className="p-6">Loading...</div>

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-slate-800">Keyword Tracking</h1>
      <p className="text-sm text-gray-500 max-w-2xl">
        Positions and search volume shown here are simulated placeholders (see{' '}
        <code>backend/app/routes/keywords.py</code>). Swap in a real SERP API (SerpApi, DataForSEO, etc.)
        for production rank tracking.
      </p>
      <KeywordTracker keywords={keywords} onChanged={refresh} />
    </div>
  )
}

export default Keywords
