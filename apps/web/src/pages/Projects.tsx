import { useEffect, useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { api, NetworkError, ApiError } from '../api/client'
import type { Project } from '../types'

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [creating, setCreating] = useState(false)

  const loadProjects = useCallback(async () => {
    setError(null)
    try {
      const data = await api.listProjects()
      setProjects(data)
    } catch (e) {
      if (e instanceof NetworkError) {
        setError('API server is not reachable. Make sure `python -m app` is running on port 8000.')
      } else if (e instanceof ApiError) {
        setError(`API error (${e.status}): ${e.body}`)
      } else {
        setError('Failed to load projects.')
      }
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadProjects()
  }, [loadProjects])

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim() || creating) return
    setCreating(true)
    try {
      await api.createProject({ name: name.trim(), description: description.trim() || undefined })
      setName('')
      setDescription('')
      setShowForm(false)
      await loadProjects()
    } catch (err) {
      if (err instanceof NetworkError) {
        setError('Cannot create project — API is unreachable.')
      } else if (err instanceof ApiError) {
        setError(`Failed to create project (${err.status}): ${err.body}`)
      }
    } finally {
      setCreating(false)
    }
  }

  async function handleDelete(id: string) {
    try {
      await api.deleteProject(id)
      await loadProjects()
    } catch {
      // silently fail on delete
    }
  }

  const statusColors: Record<string, string> = {
    draft: 'bg-gray-800 text-gray-400 border-gray-700/40',
    active: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    in_review: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    completed: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    failed: 'bg-red-500/10 text-red-400 border-red-500/20',
    archived: 'bg-gray-800 text-gray-500 border-gray-700/30',
  }

  return (
    <div className="p-6 lg:p-8 max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Projects</h1>
          <p className="text-sm text-gray-500 mt-1">
            Manage your autonomous software development projects
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium transition-all shrink-0"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          {showForm ? 'Cancel' : 'New Project'}
        </button>
      </div>

      {/* Network error banner */}
      {error && (
        <div className="flex items-start gap-3 bg-red-500/5 border border-red-500/20 rounded-xl px-5 py-4">
          <svg className="w-5 h-5 text-red-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <div className="flex-1 min-w-0">
            <p className="text-sm text-red-300">{error}</p>
            <button
              onClick={loadProjects}
              className="text-xs text-red-400/70 hover:text-red-300 mt-2 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      )}

      {/* Create form */}
      {showForm && (
        <form
          onSubmit={handleCreate}
          className="bg-gray-900/60 border border-gray-800/50 rounded-xl p-5 space-y-4"
        >
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1.5">Project Name</label>
            <input
              type="text"
              placeholder="e.g. E-commerce API"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-gray-800/60 border border-gray-700/60 rounded-lg text-sm focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 transition-all placeholder:text-gray-600"
              autoFocus
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1.5">Description (optional)</label>
            <textarea
              placeholder="Brief description of the project..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="w-full px-3.5 py-2.5 bg-gray-800/60 border border-gray-700/60 rounded-lg text-sm focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 transition-all resize-none placeholder:text-gray-600"
            />
          </div>
          <div className="flex gap-3">
            <button
              type="submit"
              disabled={!name.trim() || creating}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 disabled:cursor-not-allowed rounded-lg text-sm font-medium transition-all"
            >
              {creating ? 'Creating...' : 'Create Project'}
            </button>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm font-medium transition-all"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-24">
          <div className="flex items-center gap-3 text-gray-500">
            <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span className="text-sm">Loading projects...</span>
          </div>
        </div>
      ) : projects.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 border border-dashed border-gray-800/60 rounded-xl">
          <svg className="w-12 h-12 text-gray-700 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
          </svg>
          <p className="text-gray-500 text-sm mb-1">No projects yet</p>
          <p className="text-gray-600 text-xs">Create a project to start the autonomous development workflow.</p>
          <button
            onClick={() => setShowForm(true)}
            className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium transition-all"
          >
            Create Your First Project
          </button>
        </div>
      ) : (
        <div className="space-y-2">
          {projects.map((p) => (
            <div
              key={p.id}
              className="flex items-center justify-between bg-gray-900/40 border border-gray-800/40 rounded-xl px-5 py-4 hover:bg-gray-800/30 hover:border-gray-700/50 transition-all group"
            >
              <div className="min-w-0 flex-1">
                <Link to={`/projects/${p.id}/workflow`} className="text-sm font-medium hover:text-blue-400 transition-colors">
                  {p.name}
                </Link>
                {p.description && (
                  <p className="text-xs text-gray-500 mt-0.5 truncate max-w-lg">{p.description}</p>
                )}
              </div>
              <div className="flex items-center gap-4 shrink-0 ml-4">
                <span
                  className={`text-[11px] px-2.5 py-0.5 rounded-full border font-medium ${
                    statusColors[p.status] || 'bg-gray-800 text-gray-400 border-gray-700/40'
                  }`}
                >
                  {p.status}
                </span>
                <span className="text-[11px] text-gray-600 hidden sm:inline">
                  {new Date(p.created_at).toLocaleDateString()}
                </span>
                <Link
                  to={`/projects/${p.id}/workflow`}
                  className="text-xs text-gray-500 hover:text-gray-300 opacity-0 group-hover:opacity-100 transition-all"
                >
                  Open &rarr;
                </Link>
                <button
                  onClick={() => handleDelete(p.id)}
                  className="text-xs text-gray-600 hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100"
                  title="Delete project"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
