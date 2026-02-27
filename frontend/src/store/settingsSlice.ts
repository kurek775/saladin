import type { StateCreator } from 'zustand'

const STORAGE_KEY = 'saladin-api-keys'

type ProviderKey = 'openai' | 'anthropic' | 'google'

const HEADER_MAP: Record<ProviderKey, string> = {
  openai: 'X-OpenAI-Key',
  anthropic: 'X-Anthropic-Key',
  google: 'X-Google-Key',
}

interface StoredKeys {
  openai: string
  anthropic: string
  google: string
}

function getStoredKeys(): StoredKeys {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw)
  } catch { /* ignore */ }
  return { openai: '', anthropic: '', google: '' }
}

function persistKeys(keys: StoredKeys) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(keys))
}

export interface SettingsSlice {
  apiKeys: StoredKeys
  setApiKey: (provider: ProviderKey, key: string) => void
  clearApiKey: (provider: ProviderKey) => void
  clearAllApiKeys: () => void
  getKeyHeaders: () => Record<string, string>
}

export const createSettingsSlice: StateCreator<SettingsSlice> = (set, get) => ({
  apiKeys: getStoredKeys(),

  setApiKey: (provider, key) => {
    const updated = { ...get().apiKeys, [provider]: key }
    persistKeys(updated)
    set({ apiKeys: updated })
  },

  clearApiKey: (provider) => {
    const updated = { ...get().apiKeys, [provider]: '' }
    persistKeys(updated)
    set({ apiKeys: updated })
  },

  clearAllApiKeys: () => {
    const empty: StoredKeys = { openai: '', anthropic: '', google: '' }
    persistKeys(empty)
    set({ apiKeys: empty })
  },

  getKeyHeaders: () => {
    const keys = get().apiKeys
    const headers: Record<string, string> = {}
    for (const [provider, key] of Object.entries(keys)) {
      if (key) {
        headers[HEADER_MAP[provider as ProviderKey]] = key
      }
    }
    return headers
  },
})
