import type { StateCreator } from 'zustand'
import type { LogEntry } from '../api/types'

export interface LogSlice {
  logs: LogEntry[]
  wsConnected: boolean
  addLog: (log: LogEntry) => void
  clearLogs: () => void
  setWsConnected: (connected: boolean) => void
}

export const createLogSlice: StateCreator<LogSlice> = (set) => ({
  logs: [],
  wsConnected: false,
  addLog: (log) =>
    set((s) => ({ logs: [...s.logs.slice(-199), log] })), // Keep last 200
  clearLogs: () => set({ logs: [] }),
  setWsConnected: (connected) => set({ wsConnected: connected }),
})
