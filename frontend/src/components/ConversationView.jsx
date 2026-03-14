import React, { useState, useEffect, useRef } from 'react'
import { 
  Send, 
  User, 
  Bot, 
  Phone,
  CheckCircle,
  XCircle,
  Clock,
  UserCheck,
  Archive,
  MessageSquare
} from 'lucide-react'
import axios from 'axios'
import API_BASE from '../config/apiBase'

export default function ConversationView({ ticket, onUpdate }) {
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [sending, setSending] = useState(false)
  const [loading, setLoading] = useState(true)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    if (ticket) {
      fetchTicketDetails()
    }
  }, [ticket?.id])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const fetchTicketDetails = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE}/api/tickets/${ticket.id}`)
      setMessages(response.data.messages || [])
    } catch (error) {
      console.error('Error fetching ticket details:', error)
    } finally {
      setLoading(false)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    
    if (!newMessage.trim() || sending) return

    try {
      setSending(true)
      
      await axios.post(`${API_BASE}/api/tickets/${ticket.id}/reply`, {
        text: newMessage.trim()
      })

      setNewMessage('')
      fetchTicketDetails()
      onUpdate()
    } catch (error) {
      console.error('Error sending message:', error)
      alert('Failed to send message. Please try again.')
    } finally {
      setSending(false)
    }
  }

  const handleStatusChange = async (newStatus) => {
    try {
      await axios.put(`${API_BASE}/api/tickets/${ticket.id}/status`, {
        status: newStatus
      })
      onUpdate()
    } catch (error) {
      console.error('Error updating status:', error)
      alert('Failed to update status. Please try again.')
    }
  }

  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-white">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center">
              <User size={24} className="text-gray-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">
                {ticket.user_name || ticket.user_phone}
              </h3>
              <div className="flex items-center gap-3 text-sm text-gray-600">
                <span className="flex items-center gap-1">
                  <Phone size={14} />
                  {ticket.user_phone}
                </span>
                <span>•</span>
                <span className="capitalize">{ticket.category}</span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            {ticket.status === 'open' && (
              <button
                onClick={() => handleStatusChange('assigned')}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <UserCheck size={18} />
                Assign to Me
              </button>
            )}
            
            {ticket.status === 'assigned' && (
              <button
                onClick={() => handleStatusChange('resolved')}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                <CheckCircle size={18} />
                Resolve
              </button>
            )}
            
            {ticket.status === 'resolved' && (
              <button
                onClick={() => handleStatusChange('closed')}
                className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                <Archive size={18} />
                Close
              </button>
            )}
          </div>
        </div>

        {/* Ticket Info */}
        <div className="mt-4 flex items-center gap-4 text-sm">
          <span className={`px-3 py-1 rounded-full font-medium ${
            ticket.status === 'open' ? 'bg-yellow-100 text-yellow-800' :
            ticket.status === 'assigned' ? 'bg-blue-100 text-blue-800' :
            ticket.status === 'resolved' ? 'bg-green-100 text-green-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {ticket.status}
          </span>
          
          <span className={`px-3 py-1 rounded-full font-medium ${
            ticket.priority === 'urgent' ? 'bg-red-100 text-red-800' :
            ticket.priority === 'high' ? 'bg-orange-100 text-orange-800' :
            ticket.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
            'bg-green-100 text-green-800'
          }`}>
            {ticket.priority} priority
          </span>
          
          <span className="text-gray-600">
            Created {new Date(ticket.created_at).toLocaleString()}
          </span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <MessageSquare size={48} className="mb-4" />
            <p>No messages yet</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.direction === 'in' ? 'justify-start' : 'justify-end'}`}
            >
              <div className={`flex gap-3 max-w-2xl ${message.direction === 'out' ? 'flex-row-reverse' : ''}`}>
                {/* Avatar */}
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.direction === 'in' ? 'bg-gray-200' : 'bg-blue-600'
                }`}>
                  {message.direction === 'in' ? (
                    <User size={18} className="text-gray-600" />
                  ) : (
                    <Bot size={18} className="text-white" />
                  )}
                </div>

                {/* Message Bubble */}
                <div>
                  <div className={`px-4 py-3 rounded-lg ${
                    message.direction === 'in'
                      ? 'bg-gray-100 text-gray-900'
                      : 'bg-blue-600 text-white'
                  }`}>
                    <p className="whitespace-pre-wrap">{message.text}</p>
                    
                    {/* Intent Badge */}
                    {message.intent && message.direction === 'in' && (
                      <div className="mt-2 pt-2 border-t border-gray-200">
                        <span className="text-xs bg-white px-2 py-0.5 rounded text-gray-700">
                          {message.intent} ({Math.round(message.confidence * 100)}%)
                        </span>
                      </div>
                    )}
                  </div>
                  
                  {/* Timestamp and Status */}
                  <div className={`flex items-center gap-2 mt-1 text-xs text-gray-500 ${
                    message.direction === 'out' ? 'justify-end' : ''
                  }`}>
                    <span>{formatTime(message.created_at)}</span>
                    {message.direction === 'out' && (
                      <span className="flex items-center gap-1">
                        {message.status === 'sent' && <CheckCircle size={12} className="text-green-600" />}
                        {message.status === 'failed' && <XCircle size={12} className="text-red-600" />}
                        {message.status === 'pending' && <Clock size={12} className="text-yellow-600" />}
                        {message.status}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      {ticket.status !== 'closed' && (
        <div className="px-6 py-4 border-t border-gray-200">
          <form onSubmit={handleSendMessage} className="flex gap-3">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Type your message..."
              disabled={sending}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!newMessage.trim() || sending}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {sending ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Sending...
                </>
              ) : (
                <>
                  <Send size={18} />
                  Send
                </>
              )}
            </button>
          </form>
        </div>
      )}
    </div>
  )
}

