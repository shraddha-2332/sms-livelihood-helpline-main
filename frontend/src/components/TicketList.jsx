import React from 'react'
import { Clock, AlertCircle, CheckCircle, User, MessageSquare } from 'lucide-react'

export default function TicketList({ tickets, selectedTicket, onSelectTicket }) {
  const getStatusColor = (status) => {
    const colors = {
      open: 'bg-yellow-100 text-yellow-800',
      assigned: 'bg-blue-100 text-blue-800',
      resolved: 'bg-green-100 text-green-800',
      closed: 'bg-gray-100 text-gray-800'
    }
    return colors[status] || colors.open
  }

  const getPriorityColor = (priority) => {
    const colors = {
      urgent: 'text-red-600',
      high: 'text-orange-600',
      medium: 'text-yellow-600',
      low: 'text-green-600'
    }
    return colors[priority] || colors.medium
  }

  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now - date
    
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)
    
    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    if (days < 7) return `${days}d ago`
    
    return date.toLocaleDateString()
  }

  return (
    <div className="divide-y divide-gray-200">
      {tickets.map((ticket) => {
        const isSelected = selectedTicket?.id === ticket.id
        
        return (
          <button
            key={ticket.id}
            onClick={() => onSelectTicket(ticket)}
            className={`w-full p-4 text-left transition-colors hover:bg-gray-50 ${
              isSelected ? 'bg-blue-50 border-l-4 border-blue-600' : ''
            }`}
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className={`text-xs font-semibold ${getPriorityColor(ticket.priority)}`}>
                  #{ticket.id}
                </span>
                <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${getStatusColor(ticket.status)}`}>
                  {ticket.status}
                </span>
              </div>
              <span className="text-xs text-gray-500">
                {formatTime(ticket.updated_at)}
              </span>
            </div>

            {/* Subject */}
            <h4 className="font-medium text-gray-900 mb-1 truncate">
              {ticket.subject || 'No subject'}
            </h4>

            {/* User Info */}
            <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
              <User size={14} />
              <span>{ticket.user_name || ticket.user_phone}</span>
            </div>

            {/* Last Message Preview */}
            {ticket.last_message && (
              <div className="flex items-start gap-2 text-sm text-gray-600">
                <MessageSquare size={14} className="mt-0.5 flex-shrink-0" />
                <p className="truncate-2-lines">{ticket.last_message}</p>
              </div>
            )}

            {/* Category Badge */}
            <div className="mt-2">
              <span className="inline-block px-2 py-0.5 text-xs bg-gray-100 text-gray-700 rounded">
                {ticket.category}
              </span>
            </div>
          </button>
        )
      })}
    </div>
  )
}