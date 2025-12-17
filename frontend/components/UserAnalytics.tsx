'use client'

import { useEffect, useState } from 'react'
import { Users, TrendingUp, DollarSign, Activity, UserCheck, UserX } from 'lucide-react'
import { format } from 'date-fns'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface UserMetrics {
  user_name: string
  total_events: number
  read_events: number
  write_events: number
  high_risk_events: number
  activity_score: number
  services_used: string[]
  regions_used: string[]
  first_seen?: string
  last_seen?: string
}

interface UserCosts {
  user_name: string
  total_cost: number
  resource_count: number
  cost_per_resource: number
  service_costs?: Record<string, number>
}

interface UserAnalyticsData {
  users: Record<string, UserMetrics>
  count: number
}

export default function UserAnalytics() {
  const [userAnalytics, setUserAnalytics] = useState<UserAnalyticsData | null>(null)
  const [topUsersByUsage, setTopUsersByUsage] = useState<any[]>([])
  const [topUsersByCost, setTopUsersByCost] = useState<any[]>([])
  const [inactiveUsers, setInactiveUsers] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedUser, setSelectedUser] = useState<string | null>(null)
  const [userDetails, setUserDetails] = useState<any>(null)

  useEffect(() => {
    fetchUserAnalytics()
    const interval = setInterval(fetchUserAnalytics, 10000) // Refresh every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchUserAnalytics = async () => {
    try {
      const [analyticsRes, topUsageRes, topCostRes, inactiveRes] = await Promise.all([
        fetch(`${API_URL}/api/users/analytics`),
        fetch(`${API_URL}/api/users/top-by-usage?limit=10`),
        fetch(`${API_URL}/api/users/top-by-cost?limit=10`),
        fetch(`${API_URL}/api/users/inactive?days=30`)
      ])

      if (analyticsRes.ok) {
        const data = await analyticsRes.json()
        setUserAnalytics(data)
      }

      if (topUsageRes.ok) {
        const data = await topUsageRes.json()
        setTopUsersByUsage(data.users || [])
      }

      if (topCostRes.ok) {
        const data = await topCostRes.json()
        setTopUsersByCost(data.users || [])
      }

      if (inactiveRes.ok) {
        const data = await inactiveRes.json()
        setInactiveUsers(data.users || [])
      }
    } catch (err) {
      console.error('Error fetching user analytics:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchUserDetails = async (userName: string) => {
    try {
      const response = await fetch(`${API_URL}/api/users/${encodeURIComponent(userName)}`)
      if (response.ok) {
        const data = await response.json()
        setUserDetails(data)
        setSelectedUser(userName)
      }
    } catch (err) {
      console.error('Error fetching user details:', err)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  const totalUsers = userAnalytics?.count || 0
  const totalEvents = Object.values(userAnalytics?.users || {}).reduce(
    (sum, user: any) => sum + (user.total_events || 0),
    0
  )
  const totalCost = topUsersByCost.reduce((sum, user) => sum + (user.total_cost || 0), 0)

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Users</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{totalUsers}</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-lg">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Events</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{totalEvents.toLocaleString()}</p>
            </div>
            <div className="bg-green-100 p-3 rounded-lg">
              <Activity className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Cost</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">${totalCost.toFixed(2)}</p>
            </div>
            <div className="bg-yellow-100 p-3 rounded-lg">
              <DollarSign className="h-6 w-6 text-yellow-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Inactive Users</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{inactiveUsers.length}</p>
            </div>
            <div className="bg-red-100 p-3 rounded-lg">
              <UserX className="h-6 w-6 text-red-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Top Users Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Users by Usage */}
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <div className="flex items-center space-x-2 mb-4">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">Top Users by Activity</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Events</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Score</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {topUsersByUsage.length > 0 ? (
                  topUsersByUsage.map((user, index) => (
                    <tr
                      key={index}
                      className="hover:bg-gray-50 cursor-pointer"
                      onClick={() => fetchUserDetails(user.user_name)}
                    >
                      <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                        {user.user_name}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 text-right">
                        {user.total_events?.toLocaleString() || 0}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 text-right">
                        {user.activity_score?.toFixed(1) || '0.0'}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={3} className="px-4 py-4 text-center text-sm text-gray-500">
                      No user data available. Inject sample data to see results.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Top Users by Cost */}
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <div className="flex items-center space-x-2 mb-4">
            <DollarSign className="h-5 w-5 text-green-600" />
            <h3 className="text-lg font-semibold text-gray-900">Top Users by Cost</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Cost</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Resources</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {topUsersByCost.length > 0 ? (
                  topUsersByCost.map((user, index) => (
                    <tr
                      key={index}
                      className="hover:bg-gray-50 cursor-pointer"
                      onClick={() => fetchUserDetails(user.user_name)}
                    >
                      <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                        {user.user_name}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-green-600 font-semibold text-right">
                        ${user.total_cost?.toFixed(2) || '0.00'}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 text-right">
                        {user.resource_count || 0}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={3} className="px-4 py-4 text-center text-sm text-gray-500">
                      No cost data available. Cost attribution requires cost data.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* User Details Modal */}
      {selectedUser && userDetails && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-900">User Details: {selectedUser}</h3>
                <button
                  onClick={() => {
                    setSelectedUser(null)
                    setUserDetails(null)
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              {userDetails.metrics && (
                <div className="mb-6">
                  <h4 className="font-semibold text-gray-900 mb-3">Usage Metrics</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Total Events</p>
                      <p className="text-lg font-semibold">{userDetails.metrics.total_events?.toLocaleString() || 0}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Activity Score</p>
                      <p className="text-lg font-semibold">{userDetails.metrics.activity_score?.toFixed(1) || '0.0'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Read Events</p>
                      <p className="text-lg font-semibold">{userDetails.metrics.read_events?.toLocaleString() || 0}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Write Events</p>
                      <p className="text-lg font-semibold">{userDetails.metrics.write_events?.toLocaleString() || 0}</p>
                    </div>
                  </div>
                  {userDetails.metrics.services_used && (
                    <div className="mt-4">
                      <p className="text-sm text-gray-600 mb-2">Services Used</p>
                      <div className="flex flex-wrap gap-2">
                        {userDetails.metrics.services_used.map((service: string, idx: number) => (
                          <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
                            {service}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {userDetails.costs && (
                <div className="mb-6">
                  <h4 className="font-semibold text-gray-900 mb-3">Cost Attribution</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Total Cost</p>
                      <p className="text-lg font-semibold text-green-600">
                        ${userDetails.costs.total_cost?.toFixed(2) || '0.00'}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Resources</p>
                      <p className="text-lg font-semibold">{userDetails.costs.resource_count || 0}</p>
                    </div>
                  </div>
                </div>
              )}

              {userDetails.summary && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Usage Category</h4>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    userDetails.summary.usage_category === 'heavy' ? 'bg-red-100 text-red-800' :
                    userDetails.summary.usage_category === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {userDetails.summary.usage_category?.toUpperCase() || 'UNKNOWN'}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
