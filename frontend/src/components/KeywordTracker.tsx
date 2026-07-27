import React, { useState } from 'react'
import { ArrowDown, ArrowUp, Minus, RefreshCw, Trash2 } from 'lucide-react'
import { keywordsApi, type Keyword } from '../api/endpoints'

interface Props {
  keywords: Keyword[]
  onChanged: () => void
}

const KeywordTracker: React.FC<Props> = ({ keywords, onChanged }) => {
  const [newKeyword, setNewKeyword] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const addKeyword = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newKeyword.trim()) return
    setSubmitting(true)
    try {
      await keywordsApi.create(newKeyword.trim())
      setNewKeyword('')
      onChanged()
    } finally {
      setSubmitting(false)
    }
  }

  const trend = (k: Keyword) => {
    if (k.previous_position == null || k.position == null) return <Minus size={14} className="text-gray-400" />
    if (k.position < k.previous_position) return <ArrowUp size={14} className="text-emerald-500" />
    if (k.position > k.previous_position) return <ArrowDown size={14} className="text-red-500" />
    return <Minus size={14} className="text-gray-400" />
  }

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <h2 className="text-lg font-semibold mb-4">Keyword Tracking</h2>
      <form onSubmit={addKeyword} className="flex gap-2 mb-4">
        <input
          value={newKeyword}
          onChange={(e) => setNewKeyword(e.target.value)}
          placeholder="Add a keyword to track..."
          className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          disabled={submitting}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50"
        >
          Add
        </button>
      </form>
      <div className="space-y-2 max-h-72 overflow-y-auto">
        {keywords.length === 0 && <p className="text-sm text-gray-500">No keywords tracked yet.</p>}
        {keywords.map((k) => (
          <div key={k.id} className="flex items-center justify-between text-sm border-b border-gray-100 pb-2">
            <div className="flex items-center gap-2">
              {trend(k)}
              <span>{k.keyword}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-gray-500">
                Pos. {k.position ?? '—'} · Vol. {k.volume ?? '—'}
              </span>
              <button onClick={() => keywordsApi.refresh(k.id).then(onChanged)} title="Refresh position">
                <RefreshCw size={14} className="text-gray-400 hover:text-blue-600" />
              </button>
              <button onClick={() => keywordsApi.remove(k.id).then(onChanged)} title="Remove">
                <Trash2 size={14} className="text-gray-400 hover:text-red-600" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default KeywordTracker
