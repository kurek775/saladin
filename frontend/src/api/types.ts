export type AgentRole = 'worker' | 'supervisor'
export type AgentStatus = 'idle' | 'busy' | 'error'
export type TaskStatus = 'pending' | 'running' | 'under_review' | 'revision' | 'approved' | 'rejected' | 'failed' | 'pending_human_approval'
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
  parent_task_id: string
  depth: number
  child_task_ids: string[]
  spawned_by_agent: string
}

export interface TaskSummary {
  id: string
  description: string
  status: TaskStatus
  assigned_agents: string[]
  current_revision: number
  created_at: string
  updated_at: string
  parent_task_id: string
  depth: number
  child_task_ids: string[]
  spawned_by_agent: string
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

export interface WSTaskUpdate {
  type: 'task_update'
  data: { action: string; task: { id: string; status: TaskStatus; current_revision?: number; final_output?: string } }
}
export interface WSAgentUpdate {
  type: 'agent_update'
  data: { action: string; agent?: Agent; agent_id?: string }
}
export interface WSLog {
  type: 'log'
  data: { task_id: string; level: string; message: string; timestamp: string }
}
export interface WSWorkerOutput {
  type: 'worker_output'
  data: { task_id: string; agent_id: string; agent_name: string; output: string; revision: number; timestamp: string }
}
export interface WSSupervisorReview {
  type: 'supervisor_review'
  data: { task_id: string; decision: string; feedback: string; revision: number; timestamp: string }
}
export interface WSHumanApproval {
  type: 'human_approval_required'
  data: { task_id: string; supervisor_decision: string; supervisor_feedback: string; timestamp: string }
}
export interface WSTelemetry {
  type: 'telemetry'
  data: { task_id: string; model: string; input_tokens: number; output_tokens: number; total_tokens: number; estimated_cost_usd: number; timestamp: string }
}
export interface WSPing {
  type: 'ping'
  data: Record<string, unknown>
}

export type WSEvent = WSTaskUpdate | WSAgentUpdate | WSLog | WSWorkerOutput | WSSupervisorReview | WSHumanApproval | WSTelemetry | WSPing
