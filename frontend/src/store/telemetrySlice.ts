import type { StateCreator } from 'zustand'

export interface TokenUsage {
  model: string
  input_tokens: number
  output_tokens: number
  total_tokens: number
  estimated_cost_usd: number
  timestamp: string
}

export interface TaskTelemetry {
  total_input_tokens: number
  total_output_tokens: number
  total_tokens: number
  total_cost_usd: number
  entries: TokenUsage[]
}

export interface TelemetrySlice {
  telemetry: Record<string, TaskTelemetry>
  addTelemetryEntry: (taskId: string, entry: TokenUsage) => void
  getTaskTelemetry: (taskId: string) => TaskTelemetry
  getTotalCost: () => number
}

const emptyTelemetry: TaskTelemetry = {
  total_input_tokens: 0,
  total_output_tokens: 0,
  total_tokens: 0,
  total_cost_usd: 0,
  entries: [],
}

export const createTelemetrySlice: StateCreator<TelemetrySlice> = (set, get) => ({
  telemetry: {},

  addTelemetryEntry: (taskId, entry) => {
    set((state) => {
      const existing = state.telemetry[taskId] || { ...emptyTelemetry, entries: [] }
      return {
        telemetry: {
          ...state.telemetry,
          [taskId]: {
            total_input_tokens: existing.total_input_tokens + entry.input_tokens,
            total_output_tokens: existing.total_output_tokens + entry.output_tokens,
            total_tokens: existing.total_tokens + entry.total_tokens,
            total_cost_usd: existing.total_cost_usd + entry.estimated_cost_usd,
            entries: [...existing.entries, entry],
          },
        },
      }
    })
  },

  getTaskTelemetry: (taskId) => {
    return get().telemetry[taskId] || emptyTelemetry
  },

  getTotalCost: () => {
    return Object.values(get().telemetry).reduce((sum, t) => sum + t.total_cost_usd, 0)
  },
})
