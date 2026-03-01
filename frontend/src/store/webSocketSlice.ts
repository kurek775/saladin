import { StateCreator } from 'zustand'
import { AppStore } from './index'

export interface WebSocketSlice {
  wsConnected: boolean
  wsError: string | null
  setWsConnected: (connected: boolean) => void
  setWsError: (error: string | null) => void
}

export const createWebSocketSlice: StateCreator<AppStore, [], [], WebSocketSlice> = (set) => ({
  wsConnected: false,
  wsError: null,
  setWsConnected: (connected: boolean) => set(() => ({ wsConnected: connected })),
  setWsError: (error: string | null) => set(() => ({ wsError: error })),
})
