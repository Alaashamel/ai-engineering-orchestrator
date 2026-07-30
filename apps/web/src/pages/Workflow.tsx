import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api/client'

interface WorkflowState {
  phase: string
  phase_history: Array<{ phase: string; timestamp: string }>
  decisions: Array<{ agent: string; action: string; reasoning: string }>
  tasks: Array<{ id: string; title: string; agent: string; priority: string; status: string }>
  errors: Array<{ phase: string; error: string }>
  human_approval_needed: boolean
  pending_approvals: Array<{ id: string; action: string; risk_level: string; status: string }>
  generated_files: Array<{ path: string; agent: string; status: string; task_id: string }>
  implementation_log: Array<{ phase: string; action: string; count?: number; timestamp: string }>
}

const phaseColors: Record<string, string> = {
  discovery: 'bg-blue-500',
  planning: 'bg-purple-500',
  architecture: 'bg-orange-500',
  task_decomposition: 'bg-yellow-500',
  implementation: 'bg-green-500',
  testing: 'bg-teal-500',
  review: 'bg-pink-500',
  documentation: 'bg-indigo-500',
  deployment: 'bg-cyan-500',
  completed: 'bg-emerald-500',
  failed: 'bg-red-500',
}

export default function Workflow() {
  const { projectId } = useParams<{ projectId: string }>()
  const [state, setState] = useState<WorkflowState | null>(null)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function startWorkflow() {
    if (!projectId) return
    setRunning(true)
    setError(null)
    try {
      const result = await api.startWorkflow(projectId)
      setState(result.state as unknown as WorkflowState)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Workflow failed')
    } finally {
      setRunning(false)
    }
  }

  if (!projectId) {
    return <div className="p-6 text-gray-400">No project selected.</div>
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <Link to="/projects" className="text-sm text-blue-400 hover:text-blue-300">
            &larr; Projects
          </Link>
          <h1 className="text-2xl font-bold mt-1">Workflow</h1>
        </div>
        <button
          onClick={startWorkflow}
          disabled={running}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 rounded-lg text-sm font-medium transition-colors"
        >
          {running ? 'Running...' : 'Start Workflow'}
        </button>
      </div>

      {error && (
        <div className="bg-red-900/50 border border-red-800 rounded-xl p-4 mb-6 text-red-300 text-sm">
          {error}
        </div>
      )}

      {state && (
        <div className="space-y-6">
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
            <h2 className="text-sm font-medium text-gray-400 mb-3 uppercase tracking-wider">Phases</h2>
            <div className="space-y-2">
              {state.phase_history.map((p, i) => (
                <div key={i} className="flex items-center gap-3">
                  <span className={`w-2 h-2 rounded-full ${phaseColors[p.phase] || 'bg-gray-500'}`} />
                  <span className="text-sm capitalize">{p.phase.replace(/_/g, ' ')}</span>
                  <span className="text-xs text-gray-600 ml-auto">
                    {new Date(p.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              ))}
              <div className="flex items-center gap-3 pt-2 border-t border-gray-800">
                <span className={`w-2 h-2 rounded-full ${phaseColors[state.phase] || 'bg-gray-500'}`} />
                <span className="text-sm font-medium capitalize">
                  Current: {state.phase.replace(/_/g, ' ')}
                </span>
              </div>
            </div>
          </div>

          {state.tasks.length > 0 && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
              <h2 className="text-sm font-medium text-gray-400 mb-3 uppercase tracking-wider">
                Tasks ({state.tasks.length})
              </h2>
              <div className="space-y-2">
                {state.tasks.map((t) => (
                  <div key={t.id} className="flex items-center gap-3 text-sm">
                    <span className={`w-1.5 h-1.5 rounded-full ${
                      t.priority === 'critical' ? 'bg-red-500' :
                      t.priority === 'high' ? 'bg-orange-500' :
                      t.priority === 'medium' ? 'bg-yellow-500' : 'bg-gray-500'
                    }`} />
                    <span className="flex-1">{t.title}</span>
                    <span className="text-xs text-gray-500">{t.agent}</span>
                    <span className="text-xs px-1.5 py-0.5 rounded bg-gray-800 text-gray-400">
                      {t.priority}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {state.generated_files && state.generated_files.length > 0 && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
              <h2 className="text-sm font-medium text-gray-400 mb-3 uppercase tracking-wider">
                Generated Files ({state.generated_files.length})
              </h2>
              <div className="space-y-1 max-h-48 overflow-y-auto">
                {state.generated_files.map((f, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs">
                    <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                      f.status === 'written' ? 'bg-green-500' :
                      f.status === 'error' ? 'bg-red-500' : 'bg-gray-500'
                    }`} />
                    <span className="text-gray-300 truncate font-mono">{f.path}</span>
                    <span className="text-gray-600 ml-auto">{f.agent}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {state.implementation_log && state.implementation_log.length > 0 && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
              <h2 className="text-sm font-medium text-gray-400 mb-3 uppercase tracking-wider">
                Implementation Log
              </h2>
              <div className="space-y-1">
                {state.implementation_log.map((entry, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs">
                    <span className="text-gray-500">
                      {new Date(entry.timestamp).toLocaleTimeString()}
                    </span>
                    <span className="text-gray-300">{entry.action}</span>
                    {entry.count !== undefined && (
                      <span className="text-gray-600">({entry.count} files)</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {state.decisions.length > 0 && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
              <h2 className="text-sm font-medium text-gray-400 mb-3 uppercase tracking-wider">
                Decisions
              </h2>
              <div className="space-y-2">
                {state.decisions.map((d, i) => (
                  <div key={i} className="text-sm">
                    <span className="text-blue-400 font-medium">{d.agent}</span>
                    <span className="text-gray-500 mx-2">&rarr;</span>
                    <span>{d.action}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {state.human_approval_needed && state.pending_approvals.length > 0 && (
            <div className="bg-yellow-900/30 border border-yellow-800 rounded-xl p-4">
              <h2 className="text-sm font-medium text-yellow-400 mb-3 uppercase tracking-wider">
                Approvals Required
              </h2>
              {state.pending_approvals.map((a) => (
                <div key={a.id} className="flex items-center justify-between text-sm">
                  <span>{a.action}</span>
                  <span className={`px-2 py-0.5 rounded text-xs ${
                    a.risk_level === 'high' ? 'bg-red-900 text-red-300' :
                    a.risk_level === 'medium' ? 'bg-yellow-900 text-yellow-300' :
                    'bg-green-900 text-green-300'
                  }`}>
                    {a.risk_level} risk
                  </span>
                </div>
              ))}
            </div>
          )}

          {state.errors.length > 0 && (
            <div className="bg-red-900/30 border border-red-800 rounded-xl p-4">
              <h2 className="text-sm font-medium text-red-400 mb-3 uppercase tracking-wider">Errors</h2>
              {state.errors.map((e, i) => (
                <div key={i} className="text-sm text-red-300">
                  [{e.phase}] {e.error}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {!state && !running && (
        <div className="text-center py-12 border border-dashed border-gray-800 rounded-xl">
          <p className="text-gray-500 mb-2">No workflow has been run for this project.</p>
          <p className="text-gray-600 text-sm">Click "Start Workflow" to begin the AI engineering process.</p>
        </div>
      )}
    </div>
  )
}
