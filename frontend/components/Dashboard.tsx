'use client'

import { useEffect, useState } from 'react'
import AgentCard from './AgentCard'
import StatsCard from './StatsCard'
import EventsTable from './EventsTable'
import AnomaliesTable from './AnomaliesTable'
import { AgentStatus, DashboardStats, CloudTrailEvent, CostAnomaly } from '@/types'
import { Activity, DollarSign, AlertTriangle, TrendingUp } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface DashboardProps {
  agentStatus: AgentStatus | null
}

export default function Dashboard({ agentStatus }: DashboardProps) {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [events, setEvents] = useState<CloudTrailEvent[]>([])
  const [anomalies, setAnomalies] = useState<CostAnomaly[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
    const interval = setInterval(fetchDashboardData, 10000) // Refresh every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchDashboardData = async () => {
    try {
      const [statsRes, eventsRes, anomaliesRes] = await Promise.all([
        fetch(`${API_URL}/api/dashboard/stats`),
        fetch(`${API_URL}/api/cloudtrail/events?limit=10`),
        fetch(`${API_URL}/api/cost/anomalies?limit=10`)
      ])

      if (statsRes.ok) {
        const statsData = await statsRes.json()
        setStats(statsData)
      }

      if (eventsRes.ok) {
        const eventsData = await eventsRes.json()
        setEvents(eventsData.events || [])
      }

      if (anomaliesRes.ok) {
        const anomaliesData = await anomaliesRes.json()
        setAnomalies(anomaliesData.anomalies || [])
      }
    } catch (err) {
      console.error('Error fetching dashboard data:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="CloudTrail Events"
          value={stats?.cloudtrail.suspicious_events || 0}
          icon={Activity}
          status={stats?.cloudtrail.running ? 'active' : 'inactive'}
          subtitle={stats?.cloudtrail.last_check ? `Last check: ${new Date(stats.cloudtrail.last_check).toLocaleTimeString()}` : 'Not checked'}
        />
        <StatsCard
          title="Cost Anomalies"
          value={stats?.cost.anomalies || 0}
          icon={DollarSign}
          status={stats?.cost.running ? 'active' : 'inactive'}
          subtitle={stats?.cost.last_check ? `Last check: ${new Date(stats.cost.last_check).toLocaleTimeString()}` : 'Not checked'}
        />
        <StatsCard
          title="Active Alerts"
          value={events.length + anomalies.length}
          icon={AlertTriangle}
          status="warning"
          subtitle="Requires attention"
        />
        <StatsCard
          title="Monitoring Status"
          value={agentStatus?.orchestrator.running ? 'Active' : 'Inactive'}
          icon={TrendingUp}
          status={agentStatus?.orchestrator.running ? 'active' : 'inactive'}
          subtitle={`${agentStatus?.orchestrator.agents_count || 0} agents running`}
        />
      </div>

      {/* Agent Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {agentStatus?.agents.cloudtrail && (
          <AgentCard
            agent={agentStatus.agents.cloudtrail}
            agentName="CloudTrail Monitoring"
          />
        )}
        {agentStatus?.agents.cost && (
          <AgentCard
            agent={agentStatus.agents.cost}
            agentName="Cost Anomaly Detection"
          />
        )}
      </div>

      {/* Events and Anomalies */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <EventsTable events={events} />
        <AnomaliesTable anomalies={anomalies} />
      </div>
    </div>
  )
}
