export type AgentRole = 'worker' | 'supervisor'
export type AgentStatus = 'idle' | 'busy' | 'error'
export type TaskStatus = 'pending' | 'running' | 'under_review' | 'revision' | 'approved' | 'rejected' | 'failed'
export type SupervisorDecision = 'approve' | 'reject' | 'revise'
export type LLMProvider = '' | 'anthropic' | 'openai' | 'gemini' | 'ollama'

export interface Agent {
  id: string
  name: string
  role: AgentRole
  system_prompt: string
  llm_provider: string
  llm_model: string
  status: AgentStatus
  created_at: string
}

export interface AgentCreate {
  name: string
  role: AgentRole
  system_prompt: string
  llm_provider: string
  llm_model: string
}

export interface WorkerOutput {
  agent_id: string
  agent_name: string
  output: string
  revision: number
  timestamp: string
}

export interface SupervisorReview {
  decision: SupervisorDecision
  feedback: string
  revision: number
  timestamp: string
}

export interface Task {
  id: string
  description: string
  status: TaskStatus
  assigned_agents: string[]
  worker_outputs: WorkerOutput[]
  supervisor_reviews: SupervisorReview[]
  current_revision: number
  final_output: string
  created_at: string
  updated_at: string
}

export interface TaskSummary {
  id: string
  description: string
  status: TaskStatus
  assigned_agents: string[]
  current_revision: number
  created_at: string
  updated_at: string
}

export interface LogEntry {
  id: string
  task_id: string
  agent_id?: string
  agent_name?: string
  level: 'info' | 'error' | 'warning'
  message: string
  timestamp: string
}

export interface WSEvent {
  type: 'task_update' | 'agent_update' | 'log' | 'worker_output' | 'supervisor_review' | 'ping'
  data: Record<string, unknown>
}
