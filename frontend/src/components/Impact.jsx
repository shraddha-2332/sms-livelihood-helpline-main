import React, { useEffect, useState } from 'react'
import API_BASE from '../config/apiBase'
import { HeartHandshake, TrendingUp, Clock, Users } from 'lucide-react'

export default function Impact() {
  const [summary, setSummary] = useState(null)
  const [dashboard, setDashboard] = useState(null)

  useEffect(() => {
    fetchImpact()
  }, [])

  const fetchImpact = async () => {
    try {
      const token = localStorage.getItem('token')
      const [summaryRes, dashboardRes] = await Promise.all([
        fetch(`${API_BASE}/api/reports/summary`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_BASE}/api/analytics/dashboard?days=30`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ])
      if (summaryRes.ok) {
        const data = await summaryRes.json()
        setSummary(data)
      }
      if (dashboardRes.ok) {
        const data = await dashboardRes.json()
        setDashboard(data)
      }
    } catch (error) {
      console.error('Impact fetch error:', error)
    }
  }

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full bg-gray-50">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Impact Dashboard</h2>
          <p className="text-gray-600">Outcome-driven insights for stakeholders</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KpiCard
          title="Households Assisted"
          value={summary?.total_tickets || 0}
          icon={Users}
          color="blue"
        />
        <KpiCard
          title="Resolution Rate"
          value={`${summary?.resolution_rate || 0}%`}
          icon={TrendingUp}
          color="green"
        />
        <KpiCard
          title="Avg Response Time"
          value={`${dashboard?.avg_response_time_minutes || 0}m`}
          icon={Clock}
          color="orange"
        />
        <KpiCard
          title="Tickets Closed This Week"
          value={summary?.week_tickets || 0}
          icon={HeartHandshake}
          color="purple"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Success Story</h3>
          <p className="text-sm text-gray-700">
            “Within 24 hours, the helpline connected a small farmer with a low‑interest
            crop loan program. The family secured funding and resumed cultivation in
            time for the season.”
          </p>
          <p className="text-xs text-gray-500 mt-3">— Field Coordinator, Rural Outreach</p>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Top Urgent Issues (Last 30 Days)</h3>
          <ul className="space-y-2 text-sm text-gray-700">
            <li className="flex items-center justify-between">
              <span>Medical assistance requests</span>
              <span className="text-red-600 font-semibold">High</span>
            </li>
            <li className="flex items-center justify-between">
              <span>Food security / ration support</span>
              <span className="text-red-600 font-semibold">High</span>
            </li>
            <li className="flex items-center justify-between">
              <span>Emergency loan requests</span>
              <span className="text-orange-600 font-semibold">Medium</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}

function KpiCard({ title, value, icon: Icon, color }) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-700',
    green: 'bg-green-50 text-green-700',
    orange: 'bg-orange-50 text-orange-700',
    purple: 'bg-purple-50 text-purple-700'
  }
  return (
    <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200">
      <div className="flex items-center justify-between">
        <div className={`w-12 h-12 rounded-lg ${colorClasses[color]} flex items-center justify-center`}>
          <Icon size={22} />
        </div>
      </div>
      <div className="mt-4">
        <h3 className="text-2xl font-bold text-gray-900">{value}</h3>
        <p className="text-sm text-gray-600 mt-1">{title}</p>
      </div>
    </div>
  )
}
