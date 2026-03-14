import React, { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import AgentDashboard from './components/AgentDashboard'
import Analytics from './components/Analytics'
import VoiceRecorder from './components/VoiceRecorder'
import Reports from './components/Reports'
import Login from './components/Login'
import Registration from './components/Registration'
import { Menu, X, LogOut } from 'lucide-react'
import API_BASE from './lib/apiBase'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [agent, setAgent] = useState(null)
  const [token, setToken] = useState(null)
  const [currentView, setCurrentView] = useState('dashboard')
  const [authView, setAuthView] = useState('login') // 'login' or 'register'
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [stats, setStats] = useState({
    total: 0,
    open: 0,
    assigned: 0,
    resolved: 0
  })

  // Check for existing auth on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('token')
    const storedAgent = localStorage.getItem('agent')
    
    if (storedToken && storedAgent) {
      try {
        const agentData = JSON.parse(storedAgent)
        setToken(storedToken)
        setAgent(agentData)
        setIsAuthenticated(true)
      } catch (err) {
        console.error('Error parsing stored agent data:', err)
        localStorage.removeItem('token')
        localStorage.removeItem('agent')
      }
    }
  }, [])

  useEffect(() => {
    if (isAuthenticated) {
      fetchStats()
      // Refresh stats every 30 seconds
      const interval = setInterval(fetchStats, 30000)
      return () => clearInterval(interval)
    }
  }, [isAuthenticated])

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/tickets/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const handleLogin = (agentData, authToken) => {
    setAgent(agentData)
    setToken(authToken)
    setIsAuthenticated(true)
  }

  const handleRegister = (agentData, authToken) => {
    setAgent(agentData)
    setToken(authToken)
    setIsAuthenticated(true)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('agent')
    setToken(null)
    setAgent(null)
    setIsAuthenticated(false)
    setCurrentView('dashboard')
  }

  // Show login/registration if not authenticated
  if (!isAuthenticated) {
    if (authView === 'login') {
      return (
        <Login
          onLogin={handleLogin}
          onSwitchToRegister={() => setAuthView('register')}
        />
      )
    } else {
      return (
        <Registration
          onRegister={handleRegister}
          onSwitchToLogin={() => setAuthView('login')}
        />
      )
    }
  }

  // Authenticated view
  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-0'} transition-all duration-300 overflow-hidden`}>
        <Sidebar 
          currentView={currentView} 
          setCurrentView={setCurrentView}
          stats={stats}
        />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white shadow-sm z-10">
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  SMS Livelihood Support Helpline
                </h1>
                <p className="text-sm text-gray-600">
                  {currentView === 'dashboard' && 'Ticket Management Dashboard'}
                  {currentView === 'analytics' && 'Analytics & Reports'}
                  {currentView === 'voice' && 'Voice Call Management'}
                  {currentView === 'reports' && 'Advanced Reports'}
                </p>
              </div>
            </div>

            {/* Agent Info & Status */}
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{agent?.name}</p>
                <p className="text-xs text-gray-500">{agent?.role}</p>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 bg-green-50 rounded-full">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-green-700">Online</span>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 rounded-lg hover:bg-red-50 text-gray-600 hover:text-red-600 transition-colors"
                title="Logout"
              >
                <LogOut size={20} />
              </button>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-auto">
          {currentView === 'dashboard' && (
            <AgentDashboard onStatsUpdate={fetchStats} />
          )}
          {currentView === 'analytics' && (
            <Analytics token={token} />
          )}
          {currentView === 'voice' && (
            <VoiceRecorder />
          )}
          {currentView === 'reports' && (
            <Reports token={token} />
          )}
        </main>
      </div>
    </div>
  )
}

export default App
