'use client'

import { CostAnomaly } from '@/types'
import { format } from 'date-fns'
import { DollarSign, TrendingUp } from 'lucide-react'

interface AnomaliesTableProps {
  anomalies: CostAnomaly[]
}

export default function AnomaliesTable({ anomalies }: AnomaliesTableProps) {
  if (anomalies.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <div className="flex items-center space-x-2 mb-4">
          <DollarSign className="h-5 w-5 text-green-600" />
          <h3 className="text-lg font-semibold text-gray-900">Cost Anomalies</h3>
        </div>
        <p className="text-gray-500 text-sm">No cost anomalies detected</p>
      </div>
    )
  }

  const getImpactAmount = (impact: any): number => {
    if (typeof impact === 'object' && impact.TotalImpact) {
      return parseFloat(impact.TotalImpact.Amount || '0')
    }
    return 0
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div className="flex items-center space-x-2 mb-4">
        <TrendingUp className="h-5 w-5 text-red-600" />
        <h3 className="text-lg font-semibold text-gray-900">Recent Cost Anomalies</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Dimension
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Impact
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {anomalies.map((anomaly, index) => {
              const impact = getImpactAmount(anomaly.impact)
              return (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                    {anomaly.dimension_value || 'Unknown'}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-red-600 font-semibold">
                    ${impact.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      anomaly.status === 'OPEN' 
                        ? 'bg-yellow-100 text-yellow-800' 
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {anomaly.status || 'Unknown'}
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
