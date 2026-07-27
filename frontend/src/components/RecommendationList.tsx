import React from 'react'
import { CheckCircle2, XCircle, Circle } from 'lucide-react'
import { recommendationsApi, type Recommendation } from '../api/endpoints'

interface Props {
  recommendations: Recommendation[]
  onChanged?: () => void
}

const statusStyles: Record<string, string> = {
  pending: 'text-gray-500',
  applied: 'text-emerald-600',
  dismissed: 'text-gray-400 line-through',
}

const RecommendationList: React.FC<Props> = ({ recommendations, onChanged }) => {
  const suggestions = recommendations.filter((r) => r.type === 'suggestion')

  const handle = async (id: number, action: 'apply' | 'dismiss') => {
    if (action === 'apply') await recommendationsApi.apply(id)
    else await recommendationsApi.dismiss(id)
    onChanged?.()
  }

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <h2 className="text-lg font-semibold mb-4">Recommendations</h2>
      {suggestions.length === 0 && <p className="text-sm text-gray-500">No recommendations yet.</p>}
      <ul className="space-y-3">
        {suggestions.map((rec) => (
          <li key={rec.id} className="flex items-start justify-between gap-3">
            <div className="flex items-start gap-2">
              <Circle size={14} className={`mt-1 ${statusStyles[rec.status]}`} />
              <span className={`text-sm ${statusStyles[rec.status]}`}>{rec.suggestion}</span>
            </div>
            {rec.status === 'pending' && (
              <div className="flex gap-1 shrink-0">
                <button onClick={() => handle(rec.id, 'apply')} title="Mark as applied">
                  <CheckCircle2 size={18} className="text-emerald-500 hover:text-emerald-700" />
                </button>
                <button onClick={() => handle(rec.id, 'dismiss')} title="Dismiss">
                  <XCircle size={18} className="text-gray-400 hover:text-gray-600" />
                </button>
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default RecommendationList
