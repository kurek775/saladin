import type { Agent, AgentCreate, Task, TaskSummary } from './types'

const BASE = '/api'

async function request<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`${res.status}: ${text}`)
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

// Agents
export const fetchAgents = () => request<Agent[]>('/agents')
export const fetchAgent = (id: string) => request<Agent>(`/agents/${id}`)
export const createAgent = (data: AgentCreate) =>
  request<Agent>('/agents', { method: 'POST', body: JSON.stringify(data) })
export const updateAgent = (id: string, data: Partial<AgentCreate>) =>
  request<Agent>(`/agents/${id}`, { method: 'PATCH', body: JSON.stringify(data) })
export const deleteAgent = (id: string) =>
  request<void>(`/agents/${id}`, { method: 'DELETE' })

// Tasks
export const fetchTasks = () => request<TaskSummary[]>('/tasks')
export const fetchTask = (id: string) => request<Task>(`/tasks/${id}`)
export const createTask = (data: { description: string; assigned_agents?: string[] }) =>
  request<Task>('/tasks', { method: 'POST', body: JSON.stringify(data) })
