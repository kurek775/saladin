import type { StateCreator } from 'zustand'
import type { ResponsiveLayouts, Layout } from 'react-grid-layout'

const STORAGE_KEY = 'saladin-dashboard-layouts'

const DEFAULT_LAYOUTS: ResponsiveLayouts = {
  lg: [
    { i: 'stats', x: 0, y: 0, w: 12, h: 5, minH: 4 },
    { i: 'systemActivity', x: 0, y: 5, w: 8, h: 14, minH: 8, minW: 4 },
    { i: 'activeTasks', x: 0, y: 19, w: 8, h: 10, minH: 5, minW: 4 },
    { i: 'activeAgents', x: 8, y: 5, w: 4, h: 24, minH: 8, minW: 3 },
  ],
  md: [
    { i: 'stats', x: 0, y: 0, w: 12, h: 5, minH: 4 },
    { i: 'systemActivity', x: 0, y: 5, w: 8, h: 14, minH: 8, minW: 4 },
    { i: 'activeTasks', x: 0, y: 19, w: 8, h: 10, minH: 5, minW: 4 },
    { i: 'activeAgents', x: 8, y: 5, w: 4, h: 24, minH: 8, minW: 3 },
  ],
  sm: [
    { i: 'stats', x: 0, y: 0, w: 6, h: 9, minH: 4 },
    { i: 'systemActivity', x: 0, y: 9, w: 6, h: 14, minH: 8 },
    { i: 'activeTasks', x: 0, y: 23, w: 6, h: 10, minH: 5 },
    { i: 'activeAgents', x: 0, y: 33, w: 6, h: 12, minH: 8 },
  ],
}

function getStoredLayouts(): ResponsiveLayouts {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) return JSON.parse(stored) as ResponsiveLayouts
  } catch {
    // ignore parse errors
  }
  return DEFAULT_LAYOUTS
}

export interface DashboardSlice {
  dashboardLayouts: ResponsiveLayouts
  setDashboardLayouts: (currentLayout: Layout, allLayouts: ResponsiveLayouts) => void
  resetDashboardLayouts: () => void
}

export const createDashboardSlice: StateCreator<DashboardSlice> = (set) => ({
  dashboardLayouts: getStoredLayouts(),
  setDashboardLayouts: (_currentLayout, allLayouts) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(allLayouts))
    set({ dashboardLayouts: allLayouts })
  },
  resetDashboardLayouts: () => {
    localStorage.removeItem(STORAGE_KEY)
    set({ dashboardLayouts: DEFAULT_LAYOUTS })
  },
})
