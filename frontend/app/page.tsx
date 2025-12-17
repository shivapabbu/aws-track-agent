'use client'

import { useEffect, useState } from 'react'
import Dashboard from '@/components/Dashboard'
import UserAnalytics from '@/components/UserAnalytics'
import Header from '@/components/Header'
import { AgentStatus } from '@/types'
import { Activity, Users } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Home() {
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'dashboard' | 'users'>('dashboard')

  useEffect(() => {
    fetchAgentStatus()
    const interval = setInterval(fetchAgentStatus, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchAgentStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/health`)
      if (!response.ok) throw new Error('Failed to fetch agent status')
      const data = await response.json()
      setAgentStatus(data.agents)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <Header />
      <div className="container mx-auto px-4 py-8">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            Error: {error}
          </div>
        ) : (
          <>
            {/* Tab Navigation */}
            <div className="mb-6 border-b border-gray-200">
              <nav className="-mb-px flex space-x-8">
                <button
                  onClick={() => setActiveTab('dashboard')}
                  className={`${
                    activeTab === 'dashboard'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
                >
                  <Activity className="h-5 w-5" />
                  <span>Dashboard</span>
                </button>
                <button
                  onClick={() => setActiveTab('users')}
                  className={`${
                    activeTab === 'users'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
                >
                  <Users className="h-5 w-5" />
                  <span>User Analytics</span>
                </button>
              </nav>
            </div>

            {/* Tab Content */}
            {activeTab === 'dashboard' ? (
              <Dashboard agentStatus={agentStatus} />
            ) : (
              <UserAnalytics />
            )}
          </>
        )}
      </div>
    </main>
  )
}
