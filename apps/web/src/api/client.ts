import type { Project } from '../types'

const BASE = import.meta.env.VITE_API_URL || ''

export class ApiError extends Error {
  constructor(
    public status: number,
    public body: string,
  ) {
    super(`API ${status}: ${body}`)
    this.name = 'ApiError'
  }
}

export class NetworkError extends Error {
  constructor(cause: unknown) {
    const detail = cause instanceof Error ? `: ${cause.message}` : ''
    super(`Unable to reach the API server. Make sure the backend is running.${detail}`)
    this.name = 'NetworkError'
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${BASE}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    })
  } catch (err) {
    throw new NetworkError(err)
  }
  if (!response.ok) {
    const body = await response.text()
    throw new ApiError(response.status, body)
  }
  if (response.status === 204) return undefined as T
  return response.json()
}

export const api = {
  health: () => request<{ status: string; service: string; version: string }>('/health'),

  listProjects: () => request<Project[]>('/projects'),

  createProject: (data: { name: string; description?: string }) =>
    request<Project>('/projects', { method: 'POST', body: JSON.stringify(data) }),

  getProject: (id: string) => request<Project>(`/projects/${id}`),

  updateProject: (id: string, data: Partial<Project>) =>
    request<Project>(`/projects/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),

  deleteProject: (id: string) =>
    request<void>(`/projects/${id}`, { method: 'DELETE' }),

  startWorkflow: (projectId: string) =>
    request<{ status: string; state: Record<string, unknown> }>(
      `/workflows/${projectId}/start`, { method: 'POST' }
    ),

  approveWorkflow: (projectId: string, rollbackTo?: string) =>
    request<{ status: string; state: Record<string, unknown> }>(
      `/workflows/${projectId}/approve`, {
        method: 'POST',
        body: JSON.stringify({ rollback_to: rollbackTo }),
      }
    ),

  rejectWorkflow: (projectId: string, reason?: string, rollbackTo?: string) =>
    request<{ status: string; state: Record<string, unknown> }>(
      `/workflows/${projectId}/reject`, {
        method: 'POST',
        body: JSON.stringify({ reason: reason || '', rollback_to: rollbackTo }),
      }
    ),

  rollbackWorkflow: (projectId: string, rollbackTo: string) =>
    request<{ status: string; phase: string; phase_history: unknown[] }>(
      `/workflows/${projectId}/rollback`, {
        method: 'POST',
        body: JSON.stringify({ rollback_to: rollbackTo }),
      }
    ),

  getWorkflowStatus: (projectId: string) =>
    request<Record<string, unknown>>(`/workflows/${projectId}/status`),
}
