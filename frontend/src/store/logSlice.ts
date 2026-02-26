import type { StateCreator } from 'zustand'
import type { LogEntry } from '../api/types'

export interface LogSlice {
  logs: LogEntry[]
  addLog: (log: LogEntry) => void
  clearLogs: () => void
}

export const createLogSlice: StateCreator<LogSlice> = (set) => ({
  logs: [],
  addLog: (log) =>
    set((s) => ({ logs: [...s.logs.slice(-199), log] })), // Keep last 200
  clearLogs: () => set({ logs: [] }),
})
