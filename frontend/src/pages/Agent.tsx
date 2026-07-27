import React from 'react'
import AgentPanel from '../components/AgentPanel'

const Agent: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-slate-800">AI Agent</h1>
      <AgentPanel />
    </div>
  )
}

export default Agent
