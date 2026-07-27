import React, { useEffect, useState, useCallback } from 'react'
import { Trash2, Mail } from 'lucide-react'
import { auditsApi, reportsApi, type Audit } from '../api/endpoints'
import AuditForm from '../components/AuditForm'
import RecommendationList from '../components/RecommendationList'

const Audits: React.FC = () => {
  const [audits, setAudits] = useState<Audit[]>([])
  const [selected, setSelected] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    const res = await auditsApi.list()
    setAudits(res.data)
    setLoading(false)
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  const remove = async (id: number) => {
    await auditsApi.remove(id)
    if (selected === id) setSelected(null)
    refresh()
  }

  const emailReport = async (id: number) => {
    await reportsApi.emailAudit(id)
    alert('Report emailed (if SMTP is configured on the backend).')
  }

  if (loading) return <div className="p-6">Loading...</div>

  const selectedAudit = audits.find((a) => a.id === selected)

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-slate-800">Audits</h1>
      <AuditForm onCreated={refresh} />

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-500 text-left">
            <tr>
              <th className="px-4 py-3">URL</th>
              <th className="px-4 py-3">SEO</th>
              <th className="px-4 py-3">GEO</th>
              <th className="px-4 py-3">Date</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {audits.map((a) => (
              <tr
                key={a.id}
                className="border-t border-gray-100 hover:bg-gray-50 cursor-pointer"
                onClick={() => setSelected(a.id)}
              >
                <td className="px-4 py-3 truncate max-w-xs">{a.url}</td>
                <td className="px-4 py-3 font-medium text-blue-600">{a.seo_score}</td>
                <td className="px-4 py-3 font-medium text-emerald-600">{a.geo_score}</td>
                <td className="px-4 py-3 text-gray-500">{new Date(a.created_at).toLocaleString()}</td>
                <td className="px-4 py-3">
                  <div className="flex gap-2">
                    <button onClick={(e) => { e.stopPropagation(); emailReport(a.id) }} title="Email report">
                      <Mail size={16} className="text-gray-400 hover:text-blue-600" />
                    </button>
                    <button onClick={(e) => { e.stopPropagation(); remove(a.id) }} title="Delete">
                      <Trash2 size={16} className="text-gray-400 hover:text-red-600" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {audits.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-gray-500">
                  No audits yet — run one above.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {selectedAudit && (
        <RecommendationList recommendations={selectedAudit.recommendations} onChanged={refresh} />
      )}
    </div>
  )
}

export default Audits
