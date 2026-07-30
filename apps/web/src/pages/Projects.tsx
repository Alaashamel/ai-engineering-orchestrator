import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { Project } from '../types'

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')

  async function loadProjects() {
    try {
      const data = await api.listProjects()
      setProjects(data)
    } catch (e) {
      console.error('Failed to load projects', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadProjects()
  }, [])

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) return
    try {
      await api.createProject({ name: name.trim(), description: description.trim() || undefined })
      setName('')
      setDescription('')
      setShowForm(false)
      await loadProjects()
    } catch (err) {
      console.error('Failed to create project', err)
    }
  }

  async function handleDelete(id: string) {
    try {
      await api.deleteProject(id)
      await loadProjects()
    } catch (err) {
      console.error('Failed to delete project', err)
    }
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Projects</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium transition-colors"
        >
          {showForm ? 'Cancel' : 'New Project'}
        </button>
      </div>

      {showForm && (
        <form
          onSubmit={handleCreate}
          className="bg-gray-900 border border-gray-800 rounded-xl p-4 mb-6 space-y-3"
        >
          <input
            type="text"
            placeholder="Project name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-blue-500"
          />
          <textarea
            placeholder="Description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-blue-500 resize-none"
          />
          <button
            type="submit"
            disabled={!name.trim()}
            className="px-4 py-2 bg-green-600 hover:bg-green-500 disabled:opacity-40 rounded-lg text-sm font-medium transition-colors"
          >
            Create Project
          </button>
        </form>
      )}

      {loading ? (
        <div className="text-gray-500 text-center py-12">Loading...</div>
      ) : projects.length === 0 ? (
        <div className="text-gray-500 text-center py-12 border border-dashed border-gray-800 rounded-xl">
          No projects yet. Create one to get started.
        </div>
      ) : (
        <div className="grid gap-3">
          {projects.map((p) => (
            <div
              key={p.id}
              className="bg-gray-900 border border-gray-800 rounded-xl p-4 flex items-center justify-between"
            >
              <div>
                <h3 className="font-medium">{p.name}</h3>
                {p.description && (
                  <p className="text-sm text-gray-400 mt-1 line-clamp-1">
                    {p.description}
                  </p>
                )}
                <span className="inline-block mt-2 text-xs px-2 py-0.5 rounded-full bg-gray-800 text-gray-400">
                  {p.status}
                </span>
              </div>
              <div className="flex gap-2">
                <span className="text-xs text-gray-600">
                  {new Date(p.created_at).toLocaleDateString()}
                </span>
                <button
                  onClick={() => handleDelete(p.id)}
                  className="text-xs text-red-400 hover:text-red-300 transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
