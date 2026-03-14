import React, { useState, useEffect } from 'react'
import TicketList from './TicketList'
import ConversationView from './ConversationView'
import { Search, Filter, RefreshCw, Inbox } from 'lucide-react'
import API_BASE from '../config/apiBase'

export default function AgentDashboard({ onStatsUpdate }) {
  const [tickets, setTickets] = useState([])
  const [selectedTicket, setSelectedTicket] = useState(null)
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    status: 'all',
    priority: 'all',
    category: 'all'
  })
  const [searchQuery, setSearchQuery] = useState('')
  const [refreshing, setRefreshing] = useState(false)
  const [creatingDemo, setCreatingDemo] = useState(false)
  const [seedingDemo, setSeedingDemo] = useState(false)

  useEffect(() => {
    fetchTickets()
    // Auto-refresh every 10 seconds
    const interval = setInterval(fetchTickets, 10000)
    return () => clearInterval(interval)
  }, [filters])

  const fetchTickets = async (showRefresh = false) => {
    try {
      if (showRefresh) setRefreshing(true)
      
      const params = new URLSearchParams()
      if (filters.status !== 'all') params.append('status', filters.status)
      if (filters.priority !== 'all') params.append('priority', filters.priority)
      if (filters.category !== 'all') params.append('category', filters.category)

      const response = await fetch(`${API_BASE}/api/tickets?${params.toString()}`)
      const data = await response.json()
      
      setTickets(data.tickets || [])
      setLoading(false)
      
      if (onStatsUpdate) onStatsUpdate()
    } catch (error) {
      console.error('Error fetching tickets:', error)
      setLoading(false)
    } finally {
      setRefreshing(false)
    }
  }

  const handleRefresh = () => {
    fetchTickets(true)
  }

  const handleCreateDemoTicket = async () => {
    try {
      setCreatingDemo(true)
      const payload = {
        from: '+919834522785',
        body: 'I need information about loans for farmers'
      }
      await fetch(`${API_BASE}/webhook/sms?demo=1`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      fetchTickets(true)
    } catch (error) {
      console.error('Error creating demo ticket:', error)
      alert('Failed to create demo ticket. Please try again.')
    } finally {
      setCreatingDemo(false)
    }
  }

  const handleSeedDemoData = async () => {
    try {
      setSeedingDemo(true)
      await fetch(`${API_BASE}/api/demo/seed`, { method: 'POST' })
      fetchTickets(true)
    } catch (error) {
      console.error('Error seeding demo data:', error)
      alert('Failed to seed demo data. Please try again.')
    } finally {
      setSeedingDemo(false)
    }
  }

  const handleTicketUpdate = () => {
    fetchTickets()
    if (selectedTicket) {
      // Refresh selected ticket details
      fetch(`${API_BASE}/api/tickets/${selectedTicket.id}`)
        .then(res => res.json())
        .then(data => setSelectedTicket(data))
    }
  }

  const filteredTickets = tickets.filter(ticket => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      return (
        ticket.subject?.toLowerCase().includes(query) ||
        ticket.user_phone?.toLowerCase().includes(query) ||
        ticket.user_name?.toLowerCase().includes(query)
      )
    }
    return true
  })

  return (
    <div className="h-full flex">
      {/* Tickets List */}
      <div className="w-[420px] border-r border-gray-200 flex flex-col bg-white">
        {/* Search and Filters */}
        <div className="p-4 border-b border-gray-200 space-y-3">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              placeholder="Search tickets..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Filters */}
          <div className="flex flex-wrap gap-2">
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="flex-1 min-w-[140px] px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              <option value="open">Open</option>
              <option value="assigned">Assigned</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>

            <select
              value={filters.priority}
              onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
              className="flex-1 min-w-[140px] px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Priority</option>
              <option value="urgent">Urgent</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>

            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
              title="Refresh"
            >
              <RefreshCw size={18} className={refreshing ? 'animate-spin' : ''} />
            </button>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleCreateDemoTicket}
              disabled={creatingDemo}
              className="flex-1 px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              title="Create a demo ticket"
            >
              {creatingDemo ? 'Creating...' : 'Create Demo Ticket'}
            </button>
            <button
              onClick={handleSeedDemoData}
              disabled={seedingDemo}
              className="flex-1 px-3 py-2 text-sm bg-gray-900 text-white rounded-lg hover:bg-black disabled:opacity-50"
              title="Seed demo data"
            >
              {seedingDemo ? 'Seeding...' : 'Seed Demo Data'}
            </button>
          </div>
        </div>

        {/* Ticket List */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : filteredTickets.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-gray-500">
              <Inbox size={48} className="mb-4" />
              <p className="text-lg font-medium">No tickets found</p>
              <p className="text-sm">Try adjusting your filters</p>
            </div>
          ) : (
            <TicketList
              tickets={filteredTickets}
              selectedTicket={selectedTicket}
              onSelectTicket={setSelectedTicket}
            />
          )}
        </div>
      </div>

      {/* Conversation View */}
      <div className="flex-1">
        {selectedTicket ? (
          <ConversationView
            ticket={selectedTicket}
            onUpdate={handleTicketUpdate}
          />
        ) : (
          <div className="h-full flex items-center justify-center bg-gray-50 p-6">
            <div className="w-full max-w-2xl text-center bg-white border border-gray-200 rounded-2xl p-10 shadow-sm">
              <div className="w-24 h-24 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                <Search size={48} className="text-gray-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Select a ticket
              </h3>
              <p className="text-gray-600">
                Choose a ticket from the list to view conversation and resolution details.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

