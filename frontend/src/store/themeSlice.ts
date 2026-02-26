import type { StateCreator } from 'zustand'

export type Theme = 'light' | 'dark' | 'system'

const STORAGE_KEY = 'saladin-theme'

function applyTheme(theme: Theme) {
  const isDark =
    theme === 'dark' ||
    (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)

  document.documentElement.classList.toggle('dark', isDark)
}

function getStoredTheme(): Theme {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored === 'light' || stored === 'dark' || stored === 'system') return stored
  return 'dark'
}

export interface ThemeSlice {
  theme: Theme
  setTheme: (theme: Theme) => void
}

export const createThemeSlice: StateCreator<ThemeSlice> = (set) => {
  const initial = getStoredTheme()
  applyTheme(initial)

  return {
    theme: initial,
    setTheme: (theme) => {
      localStorage.setItem(STORAGE_KEY, theme)
      applyTheme(theme)
      set({ theme })
    },
  }
}
