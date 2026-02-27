import { useEffect, useRef } from 'react'
import { useStore } from '../store'
import type { WSEvent, TaskStatus } from '../api/types'

let idCounter = 0

export function useWebSocket(): void {
  const closedIntentionally = useRef(false)
  const instanceId = useRef(0)

  useEffect(() => {
    closedIntentionally.current = false
    const currentInstance = ++instanceId.current
    let reconnectAttempts = 0

    function getBackoffDelay(): number {
      return Math.min(1000 * Math.pow(2, reconnectAttempts), 30_000)
    }

    let ws: WebSocket | null = null

    function connect(): void {
      // Bail if this effect instance was cleaned up (React StrictMode)
      if (currentInstance !== instanceId.current) return

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      ws = new WebSocket(`${protocol}//${window.location.host}/ws`)

      ws.onopen = () => {
        reconnectAttempts = 0
        useStore.getState().setWsConnected(true)
      }

      ws.onmessage = (e: MessageEvent) => {
        try {
          const event = JSON.parse(String(e.data)) as WSEvent
          if (event.type === 'ping') {
            ws?.send(JSON.stringify({ type: 'pong' }))
            return
          }
          handleEvent(event)
        } catch {
          // ignore malformed messages
        }
      }

      ws.onclose = () => {
        useStore.getState().setWsConnected(false)
        // Only reconnect if this is still the active instance
        if (!closedIntentionally.current && currentInstance === instanceId.current) {
          const delay = getBackoffDelay()
          reconnectAttempts++
          setTimeout(connect, delay)
        }
      }

      ws.onerror = () => {}
    }

    connect()

    return () => {
      closedIntentionally.current = true
      ws?.close()
    }
  }, [])
}

function isString(value: unknown): value is string {
  return typeof value === 'string'
}

function isTaskStatus(value: unknown): value is TaskStatus {
  const statuses: ReadonlySet<string> = new Set([
    'pending', 'running', 'under_review', 'revision', 'approved', 'rejected', 'failed', 'pending_human_approval',
  ])
  return typeof value === 'string' && statuses.has(value)
}

function handleEvent(event: WSEvent): void {
  const { upsertAgent, removeAgent, updateAgentStatus, updateTask, addLog, addTelemetryEntry } =
    useStore.getState()

  switch (event.type) {
    case 'agent_update': {
      const d = event.data
      if (d.action === 'deleted' && d.agent_id) {
        removeAgent(d.agent_id)
      } else if (d.agent && d.action === 'status_changed') {
        updateAgentStatus(d.agent.id, d.agent.status)
      } else if (d.agent) {
        upsertAgent(d.agent)
      }
      break
    }
    case 'task_update': {
      const d = event.data as Record<string, unknown>
      const task = d.task as Record<string, unknown> | undefined
      const action = d.action as string | undefined
      if (task && isString(task.id) && isTaskStatus(task.status)) {
        const updates: Record<string, unknown> = {
          status: task.status,
          ...(task.current_revision !== undefined && { current_revision: task.current_revision }),
          ...(task.final_output !== undefined && { final_output: task.final_output }),
        }
        // Handle child_created: update parent's child_task_ids
        if (action === 'child_created' && Array.isArray(task.child_task_ids)) {
          updates.child_task_ids = task.child_task_ids
        }
        // Carry lineage fields if present
        if (task.parent_task_id !== undefined) updates.parent_task_id = task.parent_task_id
        if (task.depth !== undefined) updates.depth = task.depth
        if (task.child_task_ids !== undefined) updates.child_task_ids = task.child_task_ids
        if (task.spawned_by_agent !== undefined) updates.spawned_by_agent = task.spawned_by_agent

        updateTask(task.id as string, updates)
      }
      break
    }
    case 'human_approval_required': {
      const d = event.data
      updateTask(d.task_id, { status: 'pending_human_approval' })
      addLog({
        id: `${Date.now()}-${++idCounter}`,
        task_id: d.task_id,
        level: 'warning',
        message: `Human approval required — Supervisor recommends: ${d.supervisor_decision ?? '?'}`,
        timestamp: d.timestamp || new Date().toISOString(),
      })
      break
    }
    case 'telemetry': {
      const d = event.data
      addTelemetryEntry(d.task_id, {
        model: d.model || '',
        input_tokens: d.input_tokens || 0,
        output_tokens: d.output_tokens || 0,
        total_tokens: d.total_tokens || 0,
        estimated_cost_usd: d.estimated_cost_usd || 0,
        timestamp: d.timestamp || new Date().toISOString(),
      })
      break
    }
    case 'log':
    case 'worker_output':
    case 'supervisor_review': {
      // All three produce a log entry; use a common accessor pattern
      const d = event.data as Record<string, unknown>
      const agentId = d['agent_id']
      const agentName = d['agent_name']
      const taskId = d['task_id']
      const level = d['level']
      const message = d['message']
      const timestamp = d['timestamp']
      const feedback = d['feedback']
      const revision = d['revision']
      const decision = d['decision']

      let logMessage: string
      if (event.type === 'worker_output') {
        logMessage = `[Worker: ${isString(agentName) ? agentName : 'unknown'}] Output received (rev ${String(revision ?? '?')})`
      } else if (event.type === 'supervisor_review') {
        const fb = isString(feedback) ? feedback.slice(0, 100) : ''
        logMessage = `[Supervisor] Decision: ${String(decision ?? '?')} — ${fb}`
      } else {
        logMessage = isString(message) ? message : ''
      }

      addLog({
        id: `${Date.now()}-${++idCounter}`,
        task_id: isString(taskId) ? taskId : '',
        agent_id: isString(agentId) ? agentId : undefined,
        agent_name: isString(agentName) ? agentName : undefined,
        level: (level === 'info' || level === 'error' || level === 'warning') ? level : 'info',
        message: logMessage,
        timestamp: isString(timestamp) ? timestamp : new Date().toISOString(),
      })
      break
    }
  }
}
