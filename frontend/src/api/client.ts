import type { Agent, AgentCreate, Task, TaskSummary } from './types'

const BASE = '/api'

// Inject BYOK headers from store. Resolved lazily to avoid circular import at module load time.
let _storeModule: { useStore: { getState: () => { getKeyHeaders: () => Record<string, string> } } } | null = null

function getKeyHeaders(): Record<string, string> {
  if (!_storeModule) {
    // The store module is already loaded by the time any API call runs,
    // so this import() will resolve from cache synchronously in practice.
    // We assign it lazily to avoid module-level circular dependency.
    import('../store').then((m) => { _storeModule = m })
    return {}
  }
  return _storeModule.useStore.getState().getKeyHeaders()
}

async function request<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...opts,
    headers: {
      'Content-Type': 'application/json',
      ...getKeyHeaders(),
      ...opts?.headers,
    },
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
export const createTask = (data: { description: string; assigned_agents?: string[]; requires_human_approval?: boolean }) =>
  request<Task>('/tasks', { method: 'POST', body: JSON.stringify(data) })

// Approval
export const approveTask = (taskId: string, decision: { decision: string; feedback?: string }) =>
  request<Task>(`/tasks/${taskId}/approve`, { method: 'POST', body: JSON.stringify(decision) })

// Scout / Self-Improve
export const launchScout = (data: { num_tasks: number; max_depth: number; agent_id?: string }) =>
  request<{ task_id: string; status: string; num_tasks: number; max_depth: number }>(
    '/scout/launch',
    { method: 'POST', body: JSON.stringify(data) }
  )
