import { useEffect, useRef } from 'react'
import { useStore } from '../store'
import type { WSEvent, Agent, LogEntry } from '../api/types'

let idCounter = 0

export function useWebSocket() {
  const closedIntentionally = useRef(false)

  useEffect(() => {
    closedIntentionally.current = false
    let reconnectAttempts = 0

    function getBackoffDelay() {
      return Math.min(1000 * Math.pow(2, reconnectAttempts), 30_000)
    }

    let ws: WebSocket | null = null

    function connect() {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      ws = new WebSocket(`${protocol}//${window.location.host}/ws`)

      ws.onopen = () => {
        reconnectAttempts = 0
      }

      ws.onmessage = (e) => {
        try {
          const event: WSEvent = JSON.parse(e.data)
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

function handleEvent(event: WSEvent) {
  const d = event.data as Record<string, unknown>
  const { upsertAgent, removeAgent, updateAgentStatus, updateTaskStatus, addLog } =
    useStore.getState()

  switch (event.type) {
    case 'agent_update': {
      const action = d.action as string
      if (action === 'deleted') {
        removeAgent(d.agent_id as string)
      } else if (action === 'status_changed') {
        const agent = d.agent as Agent
        updateAgentStatus(agent.id, agent.status)
      } else {
        upsertAgent(d.agent as Agent)
      }
      break
    }
    case 'task_update': {
      const task = d.task as Record<string, unknown>
      if (task.status) {
        updateTaskStatus(task.id as string, task.status as string as any)
      }
      break
    }
    case 'log':
    case 'worker_output':
    case 'supervisor_review': {
      addLog({
        id: `${Date.now()}-${++idCounter}`,
        task_id: (d.task_id as string) || '',
        agent_id: (d.agent_id as string) || undefined,
        agent_name: (d.agent_name as string) || undefined,
        level: (d.level as LogEntry['level']) || 'info',
        message:
          event.type === 'worker_output'
            ? `[Worker: ${d.agent_name}] Output received (rev ${d.revision})`
            : event.type === 'supervisor_review'
              ? `[Supervisor] Decision: ${d.decision} — ${(d.feedback as string)?.slice(0, 100)}`
              : (d.message as string) || '',
        timestamp: (d.timestamp as string) || new Date().toISOString(),
      })
      break
    }
  }
}
