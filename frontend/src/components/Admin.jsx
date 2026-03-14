import React, { useEffect, useState } from 'react'
import API_BASE from '../config/apiBase'
import { UserPlus, ShieldCheck, ToggleLeft, ToggleRight } from 'lucide-react'

export default function Admin() {
  const [agents, setAgents] = useState([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({
    name: '',
    email: '',
    phone: '',
    role: 'agent',
    specialization: 'general',
    max_concurrent_tickets: 10,
    password: 'agent123'
  })

  useEffect(() => {
    fetchAgents()
  }, [])

  const fetchAgents = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/agents`)
      const data = await response.json()
      setAgents(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Error fetching agents:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleActive = async (agent) => {
    try {
      await fetch(`${API_BASE}/api/agents/${agent.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: !agent.is_active })
      })
      fetchAgents()
    } catch (error) {
      console.error('Error updating agent:', error)
    }
  }

  const handleDelete = async (agent) => {
    if (!confirm(`Delete agent ${agent.name}?`)) return
    try {
      await fetch(`${API_BASE}/api/agents/${agent.id}`, { method: 'DELETE' })
      fetchAgents()
    } catch (error) {
      console.error('Error deleting agent:', error)
      alert('Failed to delete agent.')
    }
  }

  const openEdit = (agent) => {
    setEditing({
      id: agent.id,
      name: agent.name,
      email: agent.email,
      phone: agent.phone || '',
      role: agent.role,
      specialization: agent.specialization,
      max_concurrent_tickets: agent.max_concurrent_tickets || 10,
      password: '',
      is_active: agent.is_active
    })
  }

  const submitEdit = async (e) => {
    e.preventDefault()
    try {
      await fetch(`${API_BASE}/api/agents/${editing.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editing)
      })
      setEditing(null)
      fetchAgents()
    } catch (error) {
      console.error('Error updating agent:', error)
      alert('Failed to update agent.')
    }
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    try {
      setCreating(true)
      const response = await fetch(`${API_BASE}/api/agents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      })
      if (!response.ok) {
        const err = await response.json().catch(() => ({}))
        throw new Error(err.error || 'Failed to create agent')
      }
      setForm({
        name: '',
        email: '',
        phone: '',
        role: 'agent',
        specialization: 'general',
        max_concurrent_tickets: 10,
        password: 'agent123'
      })
      fetchAgents()
    } catch (error) {
      console.error('Error creating agent:', error)
      alert(error.message || 'Failed to create agent. Please try again.')
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full bg-gray-50">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Admin Panel</h2>
          <p className="text-gray-600">Manage agents and access controls</p>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <ShieldCheck size={18} />
          Admin Access
        </div>
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Create Agent</h3>
        <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            type="text"
            placeholder="Full name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
          <input
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
          <input
            type="tel"
            placeholder="Phone (optional)"
            value={form.phone}
            onChange={(e) => setForm({ ...form, phone: e.target.value })}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <select
            value={form.role}
            onChange={(e) => setForm({ ...form, role: e.target.value })}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="agent">Agent</option>
            <option value="supervisor">Supervisor</option>
            <option value="admin">Admin</option>
          </select>
          <select
            value={form.specialization}
            onChange={(e) => setForm({ ...form, specialization: e.target.value })}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="general">General</option>
            <option value="agriculture">Agriculture</option>
            <option value="finance">Finance</option>
            <option value="training">Training</option>
            <option value="employment">Employment</option>
          </select>
          <input
            type="number"
            min="1"
            max="50"
            placeholder="Max tickets"
            value={form.max_concurrent_tickets}
            onChange={(e) => setForm({ ...form, max_concurrent_tickets: Number(e.target.value) })}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            placeholder="Password (default: agent123)"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 md:col-span-3"
          />
          <button
            type="submit"
            disabled={creating}
            className="md:col-span-3 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <UserPlus size={18} />
            {creating ? 'Creating...' : 'Add Agent'}
          </button>
        </form>
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Agents</h3>
        {loading ? (
          <div className="text-gray-500">Loading...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 text-left text-gray-500">
                  <th className="py-2">Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Specialization</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {agents.map(agent => (
                  <tr key={agent.id} className="border-b border-gray-100">
                    <td className="py-2 font-medium text-gray-900">{agent.name}</td>
                    <td>{agent.email}</td>
                    <td className="capitalize">{agent.role}</td>
                    <td className="capitalize">{agent.specialization}</td>
                    <td>
                      <span className={`px-2 py-0.5 rounded-full text-xs ${agent.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                        {agent.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="flex gap-2 py-2">
                      <button
                        onClick={() => openEdit(agent)}
                        className="inline-flex items-center gap-1 text-xs px-2 py-1 border border-gray-200 rounded hover:bg-gray-50"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(agent)}
                        className="inline-flex items-center gap-1 text-xs px-2 py-1 border border-red-200 text-red-600 rounded hover:bg-red-50"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {editing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Edit Agent</h3>
            <form onSubmit={submitEdit} className="space-y-3">
              <input
                type="text"
                value={editing.name}
                onChange={(e) => setEditing({ ...editing, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="Name"
                required
              />
              <input
                type="email"
                value={editing.email}
                onChange={(e) => setEditing({ ...editing, email: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="Email"
                required
              />
              <input
                type="tel"
                value={editing.phone}
                onChange={(e) => setEditing({ ...editing, phone: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="Phone"
              />
              <div className="grid grid-cols-2 gap-3">
                <select
                  value={editing.role}
                  onChange={(e) => setEditing({ ...editing, role: e.target.value })}
                  className="px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="agent">Agent</option>
                  <option value="supervisor">Supervisor</option>
                  <option value="admin">Admin</option>
                </select>
                <select
                  value={editing.specialization}
                  onChange={(e) => setEditing({ ...editing, specialization: e.target.value })}
                  className="px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="general">General</option>
                  <option value="agriculture">Agriculture</option>
                  <option value="finance">Finance</option>
                  <option value="training">Training</option>
                  <option value="employment">Employment</option>
                </select>
              </div>
              <label className="flex items-center gap-2 text-sm text-gray-700">
                <input
                  type="checkbox"
                  checked={editing.is_active ?? true}
                  onChange={(e) => setEditing({ ...editing, is_active: e.target.checked })}
                />
                Active agent
              </label>
              <input
                type="number"
                min="1"
                max="50"
                value={editing.max_concurrent_tickets}
                onChange={(e) => setEditing({ ...editing, max_concurrent_tickets: Number(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="Max concurrent tickets"
              />
              <input
                type="text"
                value={editing.password}
                onChange={(e) => setEditing({ ...editing, password: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="New password (optional)"
              />
              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setEditing(null)}
                  className="px-4 py-2 bg-gray-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg"
                >
                  Save
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
