import React from 'react'
import { 
  LayoutDashboard, 
  BarChart3, 
  Phone, 
  Users, 
  Settings,
  Inbox,
  CheckCircle,
  Clock,
  AlertCircle,
  FileText
} from 'lucide-react'

export default function Sidebar({ currentView, setCurrentView, stats }) {
  const navigation = [
    { 
      name: 'Dashboard', 
      icon: LayoutDashboard, 
      view: 'dashboard',
      description: 'Ticket management'
    },
    { 
      name: 'Analytics', 
      icon: BarChart3, 
      view: 'analytics',
      description: 'Reports & insights'
    },
    {
      name: 'Impact',
      icon: Users,
      view: 'impact',
      description: 'Outcomes & stories'
    },
    { 
      name: 'Voice Calls', 
      icon: Phone, 
      view: 'voice',
      description: 'Voice management'
    },
    {
      name: 'Reports',
      icon: FileText,
      view: 'reports',
      description: 'Advanced reports'
    }
  ]

  return (
    <div className="h-full bg-white border-r border-gray-200 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
            <Phone className="text-white" size={24} />
          </div>
          <div>
            <h2 className="font-bold text-gray-900">Helpline</h2>
            <p className="text-xs text-gray-500">Agent Portal</p>
          </div>
        </div>
      </div>

      {/* Stats Summary */}
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-xs font-semibold text-gray-500 uppercase mb-3">
          Quick Stats
        </h3>
        <div className="space-y-2">
          <StatItem 
            icon={Inbox} 
            label="Total" 
            value={stats.total} 
            color="blue"
          />
          <StatItem 
            icon={AlertCircle} 
            label="Open" 
            value={stats.open} 
            color="yellow"
          />
          <StatItem 
            icon={Clock} 
            label="Assigned" 
            value={stats.assigned} 
            color="orange"
          />
          <StatItem 
            icon={CheckCircle} 
            label="Resolved" 
            value={stats.resolved} 
            color="green"
          />
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navigation.map((item) => {
            const Icon = item.icon
            const isActive = currentView === item.view
            
            return (
              <li key={item.name}>
                <button
                  onClick={() => setCurrentView(item.view)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-blue-50 text-blue-700'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <Icon size={20} />
                  <div className="text-left">
                    <div className="font-medium">{item.name}</div>
                    <div className="text-xs text-gray-500">{item.description}</div>
                  </div>
                </button>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center gap-3 px-3 py-2">
          <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
            <Users size={16} className="text-gray-600" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-900">Agent User</p>
            <p className="text-xs text-gray-500">Online</p>
          </div>
          <button className="p-1 hover:bg-gray-100 rounded">
            <Settings size={18} className="text-gray-600" />
          </button>
        </div>
      </div>
    </div>
  )
}

function StatItem({ icon: Icon, label, value, color }) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-700',
    yellow: 'bg-yellow-50 text-yellow-700',
    orange: 'bg-orange-50 text-orange-700',
    green: 'bg-green-50 text-green-700'
  }

  return (
    <div className={`flex items-center justify-between px-3 py-2 rounded-lg ${colorClasses[color]}`}>
      <div className="flex items-center gap-2">
        <Icon size={16} />
        <span className="text-sm font-medium">{label}</span>
      </div>
      <span className="text-lg font-bold">{value}</span>
    </div>
  )
}
