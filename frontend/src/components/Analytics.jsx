import React, { useState, useEffect } from 'react'
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts'
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  MessageSquare,
  CheckCircle,
  Clock
} from 'lucide-react'
import API_BASE from '../lib/apiBase'

export default function Analytics() {
  const [analytics, setAnalytics] = useState(null)
  const [intents, setIntents] = useState(null)
  const [performance, setPerformance] = useState(null)
  const [timeRange, setTimeRange] = useState(7)

  useEffect(() => {
    fetchAnalytics()
    fetchIntents()
    fetchPerformance()
  }, [timeRange])

  const fetchAnalytics = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_BASE}/api/analytics/dashboard?days=${timeRange}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (response.ok) {
        const data = await response.json()
        setAnalytics(data)
      }
    } catch (error) {
      console.error('Failed to fetch analytics:', error)
    }
  }

  const fetchIntents = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_BASE}/api/analytics/intents?days=${timeRange}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (response.ok) {
        const data = await response.json()
        setIntents(data)
      }
    } catch (error) {
      console.error('Failed to fetch intents:', error)
    }
  }

  const fetchPerformance = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_BASE}/api/analytics/performance?days=${timeRange}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (response.ok) {
        const data = await response.json()
        setPerformance(data)
      }
    } catch (error) {
      console.error('Failed to fetch performance:', error)
    }
  }

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full bg-gray-50">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Analytics & Reports</h2>
          <p className="text-gray-600">System performance and insights</p>
        </div>

        {/* Time Range Selector */}
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(Number(e.target.value))}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Messages"
          value={analytics?.messages?.total || 0}
          change={+12.5}
          icon={MessageSquare}
          color="blue"
        />
        <MetricCard
          title="Active Users"
          value={analytics?.users?.active || 0}
          change={+8.2}
          icon={Users}
          color="green"
        />
        <MetricCard
          title="Resolution Rate"
          value={`${analytics?.tickets?.resolution_rate || 0}%`}
          change={+5.3}
          icon={CheckCircle}
          color="purple"
        />
        <MetricCard
          title="Avg Response Time"
          value={`${analytics?.avg_response_time_minutes || 0}m`}
          change={-3.1}
          icon={Clock}
          color="orange"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Trend */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Message Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={analytics?.daily_trend || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Intent Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Intent Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={intents?.intents || []}
                dataKey="count"
                nameKey="intent"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label
              >
                {(intents?.intents || []).map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Intent Details Table */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Intent Classification Details</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Intent</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700">Count</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700">Percentage</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700">Avg Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {(intents?.intents || []).map((intent, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-900">{intent.intent}</td>
                  <td className="px-4 py-3 text-sm text-gray-600 text-right">{intent.count}</td>
                  <td className="px-4 py-3 text-sm text-gray-600 text-right">{intent.percentage}%</td>
                  <td className="px-4 py-3 text-sm text-gray-600 text-right">
                    {(intent.avg_confidence * 100).toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">System Performance</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">
              {performance?.message_success_rate || 0}%
            </div>
            <div className="text-sm text-gray-600 mt-1">Message Success Rate</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">
              {performance?.avg_response_time_minutes || 0}m
            </div>
            <div className="text-sm text-gray-600 mt-1">Avg Response Time</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">
              {performance?.avg_ticket_resolution_hours || 0}h
            </div>
            <div className="text-sm text-gray-600 mt-1">Avg Resolution Time</div>
          </div>
        </div>
      </div>
    </div>
  )
}

function MetricCard({ title, value, change, icon: Icon, color }) {
  const isPositive = change > 0
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    orange: 'bg-orange-50 text-orange-600'
  }

  return (
    <div className="card card-hover">
      <div className="flex items-center justify-between">
        <div className={`w-12 h-12 rounded-lg ${colorClasses[color]} flex items-center justify-center`}>
          <Icon size={24} />
        </div>
        <div className={`flex items-center gap-1 text-sm font-medium ${
          isPositive ? 'text-green-600' : 'text-red-600'
        }`}>
          {isPositive ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
          {Math.abs(change)}%
        </div>
      </div>
      <div className="mt-4">
        <h3 className="text-2xl font-bold text-gray-900">{value}</h3>
        <p className="text-sm text-gray-600 mt-1">{title}</p>
      </div>
    </div>
  )
}
