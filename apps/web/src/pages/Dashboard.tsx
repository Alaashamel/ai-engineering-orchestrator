import { useEffect, useState } from 'react'
import { api } from '../api/client'

interface HealthStatus {
  status: string
  service: string
  version: string
}

export default function Dashboard() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .health()
      .then(setHealth)
      .catch((e: Error) => setError(e.message))
  }, [])

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <div className="text-sm text-gray-400 mb-1">API Status</div>
          {health ? (
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500" />
              <span className="text-green-400 font-medium">Operational</span>
            </div>
          ) : error ? (
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-red-500" />
              <span className="text-red-400 font-medium">Error</span>
            </div>
          ) : (
            <div className="text-gray-500">Connecting...</div>
          )}
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <div className="text-sm text-gray-400 mb-1">Projects</div>
          <div className="text-2xl font-bold">0</div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <div className="text-sm text-gray-400 mb-1">Active Agents</div>
          <div className="text-2xl font-bold">0</div>
        </div>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h2 className="text-lg font-semibold mb-3">Welcome</h2>
        <p className="text-gray-400 leading-relaxed">
          This is the AI Software Engineering Company control center. Create a
          project to start the autonomous software development workflow. The
          system will analyze requirements, design architecture, assign tasks to
          specialized AI agents, and generate a complete, tested, documented,
          and deployment-ready project.
        </p>
        {health && (
          <p className="text-xs text-gray-600 mt-4">
            API: {health.service} v{health.version}
          </p>
        )}
      </div>
    </div>
  )
}
