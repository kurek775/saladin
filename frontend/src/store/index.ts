import { create } from 'zustand'
import { createAgentSlice, type AgentSlice } from './agentSlice'
import { createTaskSlice, type TaskSlice } from './taskSlice'
import { createLogSlice, type LogSlice } from './logSlice'
import { createThemeSlice, type ThemeSlice } from './themeSlice'

export type AppStore = AgentSlice & TaskSlice & LogSlice & ThemeSlice

export const useStore = create<AppStore>()((...a) => ({
  ...createAgentSlice(...a),
  ...createTaskSlice(...a),
  ...createLogSlice(...a),
  ...createThemeSlice(...a),
}))
