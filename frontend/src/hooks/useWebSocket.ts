import { useEffect, useRef } from 'react'
import { useStore } from '../store'
import type { WSEvent, Agent, LogEntry, TaskStatus } from '../api/types'

let idCounter = 0

export function useWebSocket(): void {
  const closedIntentionally = useRef(false)

  useEffect(() => {
    closedIntentionally.current = false
    let reconnectAttempts = 0

    function getBackoffDelay(): number {
      return Math.min(1000 * Math.pow(2, reconnectAttempts), 30_000)
    }

    let ws: WebSocket | null = null

    function connect(): void {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      ws = new WebSocket(`${protocol}//${window.location.host}/ws`)

      ws.onopen = () => {
        reconnectAttempts = 0
      }

      ws.onmessage = (e: MessageEvent) => {
        try {
          const event = JSON.parse(String(e.data)) as WSEvent
          if (event.type === 'ping') return
          handleEvent(event)
        } catch {
          // ignore malformed messages
        }
      }

      ws.onclose = () => {
        if (!closedIntentionally.current) {
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

function isAgent(value: unknown): value is Agent {
  return typeof value === 'object' && value !== null && 'id' in value && 'status' in value
}

function isTaskStatus(value: unknown): value is TaskStatus {
  const statuses: ReadonlySet<string> = new Set(['pending', 'running', 'under_review', 'revision', 'approved', 'rejected', 'failed'])
  return typeof value === 'string' && statuses.has(value)
}

function handleEvent(event: WSEvent): void {
  const d = event.data
  const { upsertAgent, removeAgent, updateAgentStatus, updateTaskStatus, addLog } =
    useStore.getState()

  switch (event.type) {
    case 'agent_update': {
      const action = d['action']
      if (action === 'deleted' && isString(d['agent_id'])) {
        removeAgent(d['agent_id'])
      } else if (action === 'status_changed' && isAgent(d['agent'])) {
        updateAgentStatus(d['agent'].id, d['agent'].status)
      } else if (isAgent(d['agent'])) {
        upsertAgent(d['agent'])
      }
      break
    }
    case 'task_update': {
      const task = d['task']
      if (typeof task === 'object' && task !== null) {
        const taskObj = task as Record<string, unknown>
        const taskId = taskObj['id']
        const taskStatus = taskObj['status']
        if (isString(taskId) && isTaskStatus(taskStatus)) {
          updateTaskStatus(taskId, taskStatus)
        }
      }
      break
    }
    case 'log':
    case 'worker_output':
    case 'supervisor_review': {
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

      const entry: LogEntry = {
        id: `${Date.now()}-${++idCounter}`,
        task_id: isString(taskId) ? taskId : '',
        agent_id: isString(agentId) ? agentId : undefined,
        agent_name: isString(agentName) ? agentName : undefined,
        level: (level === 'info' || level === 'error' || level === 'warning') ? level : 'info',
        message: logMessage,
        timestamp: isString(timestamp) ? timestamp : new Date().toISOString(),
      }
      addLog(entry)
      break
    }
  }
}
