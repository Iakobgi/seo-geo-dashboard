import React from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import type { Audit } from '../api/endpoints'

const COLORS = ['#3b82f6', '#10b981']

const SEOScoreCard: React.FC<{ audit?: Audit }> = ({ audit }) => {
  if (!audit) {
    return (
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h2 className="text-lg font-semibold mb-2">Latest Audit</h2>
        <p className="text-gray-500 text-sm">Run your first audit to see scores here.</p>
      </div>
    )
  }

  const data = [
    { name: 'SEO', value: audit.seo_score },
    { name: 'GEO', value: audit.geo_score },
  ]

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <h2 className="text-lg font-semibold mb-1">Latest Audit</h2>
      <p className="text-sm text-gray-500 mb-4 truncate">{audit.url}</p>
      <ResponsiveContainer width="100%" height={200}>
        <PieChart>
          <Pie data={data} cx="50%" cy="50%" innerRadius={45} outerRadius={80} dataKey="value" label>
            {data.map((entry, index) => (
              <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
      <div className="flex justify-around mt-2 text-sm">
        <div>
          <span className="font-semibold text-blue-600">{audit.seo_score}</span> SEO
        </div>
        <div>
          <span className="font-semibold text-emerald-600">{audit.geo_score}</span> GEO
        </div>
      </div>
    </div>
  )
}

export default SEOScoreCard
