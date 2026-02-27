import { create } from 'zustand'
import { createAgentSlice, type AgentSlice } from './agentSlice'
import { createTaskSlice, type TaskSlice } from './taskSlice'
import { createLogSlice, type LogSlice } from './logSlice'
import { createThemeSlice, type ThemeSlice } from './themeSlice'
import { createDashboardSlice, type DashboardSlice } from './dashboardSlice'
import { createSettingsSlice, type SettingsSlice } from './settingsSlice'
import { createTelemetrySlice, type TelemetrySlice } from './telemetrySlice'

export type AppStore = AgentSlice & TaskSlice & LogSlice & ThemeSlice & DashboardSlice & SettingsSlice & TelemetrySlice

export const useStore = create<AppStore>()((...a) => ({
  ...createAgentSlice(...a),
  ...createTaskSlice(...a),
  ...createLogSlice(...a),
  ...createThemeSlice(...a),
  ...createDashboardSlice(...a),
  ...createSettingsSlice(...a),
  ...createTelemetrySlice(...a),
}))
