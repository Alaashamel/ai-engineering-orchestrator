import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'

interface HealthStatus {
  status: string
  service: string
  version: string
}

interface Project {
  id: string
  name: string
  description: string | null
  status: string
  created_at: string
}

type ConnState = 'loading' | 'connected' | 'error'

export default function Dashboard() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [projects, setProjects] = useState<Project[]>([])
  const [connState, setConnState] = useState<ConnState>('loading')
  const [healthError, setHealthError] = useState<string | null>(null)

  useEffect(() => {
    api
      .health()
      .then((h) => {
        setHealth(h)
        setConnState('connected')
      })
      .catch((e: Error) => {
        setHealthError(e.message)
        setConnState('error')
      })
    api
      .listProjects()
      .then(setProjects)
      .catch(() => {})
  }, [])

  const statusColor =
    connState === 'connected'
      ? 'bg-emerald-500'
      : connState === 'loading'
        ? 'bg-amber-500'
        : 'bg-red-500'

  const statusLabel =
    connState === 'connected'
      ? 'Operational'
      : connState === 'loading'
        ? 'Connecting...'
        : 'Degraded'

  const activeProjects = projects.filter((p) => p.status !== 'archived' && p.status !== 'completed').length
  const completedProjects = projects.filter((p) => p.status === 'completed').length

  return (
    <div className="p-6 lg:p-8 max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">
          System overview and quick actions
        </p>
      </div>

      {/* Status cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-gray-900/60 border border-gray-800/50 rounded-xl p-5 hover:border-gray-700/50 transition-colors">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">API Status</span>
            <span className={`w-2 h-2 rounded-full ${statusColor} shadow-lg shadow-${statusColor}/20`} />
          </div>
          <div className={`text-lg font-semibold ${connState === 'error' ? 'text-red-400' : 'text-gray-100'}`}>
            {statusLabel}
          </div>
          {health && (
            <div className="text-[11px] text-gray-600 mt-2">
              {health.service} v{health.version}
            </div>
          )}
          {healthError && (
            <div className="text-[11px] text-red-500/70 mt-2 truncate" title={healthError}>
              {healthError}
            </div>
          )}
        </div>

        <div className="bg-gray-900/60 border border-gray-800/50 rounded-xl p-5 hover:border-gray-700/50 transition-colors">
          <div className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">Active Projects</div>
          <div className="text-3xl font-bold text-gray-100">{activeProjects}</div>
          <div className="text-[11px] text-gray-600 mt-2">
            {completedProjects} completed
          </div>
        </div>

        <div className="bg-gray-900/60 border border-gray-800/50 rounded-xl p-5 hover:border-gray-700/50 transition-colors">
          <div className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">Active Agents</div>
          <div className="text-3xl font-bold text-gray-100">0</div>
          <div className="text-[11px] text-gray-600 mt-2">Waiting for workflow</div>
        </div>

        <div className="bg-gray-900/60 border border-gray-800/50 rounded-xl p-5 hover:border-gray-700/50 transition-colors">
          <div className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">Database</div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-red-500 shadow-lg shadow-red-500/20" />
            <span className="text-lg font-semibold text-red-400">Unavailable</span>
          </div>
          <div className="text-[11px] text-gray-600 mt-2">PostgreSQL required</div>
        </div>
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent projects / welcome */}
        <div className="lg:col-span-2 space-y-6">
          {/* Welcome card */}
          <div className="bg-gradient-to-br from-gray-900 to-gray-900/40 border border-gray-800/50 rounded-xl p-6">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white shrink-0 mt-1">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <h2 className="text-lg font-semibold">Welcome to AI Software Engineering Co.</h2>
                <p className="text-sm text-gray-400 leading-relaxed mt-2">
                  This control center manages autonomous software development workflows.
                  Create a project to start — the system will analyze requirements,
                  design architecture, assign tasks to specialized AI agents, and
                  generate complete, tested, and deployment-ready code.
                </p>
                <div className="flex gap-3 mt-4">
                  <Link
                    to="/projects"
                    className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                    </svg>
                    New Project
                  </Link>
                  {connState === 'error' && (
                    <button
                      onClick={() => window.location.reload()}
                      className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm font-medium transition-colors"
                    >
                      Retry Connection
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Recent projects list */}
          {projects.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">
                Recent Projects
              </h3>
              <div className="space-y-2">
                {projects.slice(0, 5).map((p) => (
                  <Link
                    key={p.id}
                    to={`/projects/${p.id}/workflow`}
                    className="flex items-center justify-between bg-gray-900/40 border border-gray-800/40 rounded-lg px-4 py-3 hover:bg-gray-800/40 hover:border-gray-700/50 transition-all"
                  >
                    <div className="min-w-0">
                      <div className="text-sm font-medium truncate">{p.name}</div>
                      {p.description && (
                        <div className="text-xs text-gray-500 truncate mt-0.5">{p.description}</div>
                      )}
                    </div>
                    <div className="flex items-center gap-3 shrink-0 ml-4">
                      <span className="text-[11px] px-2 py-0.5 rounded-full bg-gray-800 text-gray-400 capitalize border border-gray-700/40">
                        {p.status}
                      </span>
                      <span className="text-[11px] text-gray-600">
                        {new Date(p.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Quick info sidebar */}
        <div className="space-y-4">
          <div className="bg-gray-900/40 border border-gray-800/50 rounded-xl p-5">
            <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">Quick Start</h3>
            <ol className="space-y-3 text-sm text-gray-400">
              <li className="flex gap-3">
                <span className="w-5 h-5 rounded-full bg-blue-500/10 text-blue-400 text-[11px] font-bold flex items-center justify-center shrink-0 mt-0.5">1</span>
                <span>Create a project with requirements</span>
              </li>
              <li className="flex gap-3">
                <span className="w-5 h-5 rounded-full bg-blue-500/10 text-blue-400 text-[11px] font-bold flex items-center justify-center shrink-0 mt-0.5">2</span>
                <span>AI agents analyze and design architecture</span>
              </li>
              <li className="flex gap-3">
                <span className="w-5 h-5 rounded-full bg-blue-500/10 text-blue-400 text-[11px] font-bold flex items-center justify-center shrink-0 mt-0.5">3</span>
                <span>Code is generated, tested, and reviewed</span>
              </li>
              <li className="flex gap-3">
                <span className="w-5 h-5 rounded-full bg-blue-500/10 text-blue-400 text-[11px] font-bold flex items-center justify-center shrink-0 mt-0.5">4</span>
                <span>Final approval before deployment</span>
              </li>
            </ol>
          </div>

          <div className="bg-gray-900/40 border border-gray-800/50 rounded-xl p-5">
            <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">System</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">API</span>
                <span className={connState === 'connected' ? 'text-emerald-400' : 'text-red-400'}>
                  {connState === 'connected' ? 'Online' : 'Offline'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Database</span>
                <span className="text-red-400">Offline</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">LLM Provider</span>
                <span className="text-amber-400">Mock Mode</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
