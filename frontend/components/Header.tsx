'use client'

import { Activity, Shield, DollarSign } from 'lucide-react'

export default function Header() {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-blue-600 p-2 rounded-lg">
              <Shield className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">AWS Track Agent</h1>
              <p className="text-sm text-gray-500">Continuous Monitoring & Anomaly Detection</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Activity className="h-4 w-4" />
              <span>24/7 Monitoring</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
