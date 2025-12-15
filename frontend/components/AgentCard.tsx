'use client'

import { CheckCircle2, XCircle, Clock } from 'lucide-react'
import { Agent } from '@/types'
import { format } from 'date-fns'

interface AgentCardProps {
  agent: Agent
  agentName: string
}

export default function AgentCard({ agent, agentName }: AgentCardProps) {
  const isRunning = agent.running
  const statusColor = isRunning ? 'text-green-600' : 'text-red-600'
  const statusBg = isRunning ? 'bg-green-50' : 'bg-red-50'
  const StatusIcon = isRunning ? CheckCircle2 : XCircle

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{agentName}</h3>
        <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${statusBg}`}>
          <StatusIcon className={`h-4 w-4 ${statusColor}`} />
          <span className={`text-sm font-medium ${statusColor}`}>
            {isRunning ? 'Running' : 'Stopped'}
          </span>
        </div>
      </div>

      <div className="space-y-3">
        {agent.last_check_time && (
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Clock className="h-4 w-4" />
            <span>Last check: {format(new Date(agent.last_check_time), 'PPp')}</span>
          </div>
        )}

        {agent.status && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-2 gap-4 text-sm">
              {Object.entries(agent.status).map(([key, value]) => (
                <div key={key}>
                  <span className="text-gray-500 capitalize">{key.replace(/_/g, ' ')}:</span>
                  <span className="ml-2 font-medium text-gray-900">
                    {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : String(value)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
