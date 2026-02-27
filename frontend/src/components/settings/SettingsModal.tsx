import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Eye, EyeOff, CheckCircle, XCircle, Loader2, Trash2 } from 'lucide-react'
import { useStore } from '../../store'
import { cn } from '../../utils'

const PROVIDERS = [
  { key: 'openai' as const, label: 'OpenAI', placeholder: 'sk-...' },
  { key: 'anthropic' as const, label: 'Anthropic', placeholder: 'sk-ant-...' },
  { key: 'google' as const, label: 'Google', placeholder: 'AIza...' },
]

interface Props {
  open: boolean
  onClose: () => void
}

export function SettingsModal({ open, onClose }: Props) {
  const { apiKeys, setApiKey, clearAllApiKeys } = useStore()
  const [visible, setVisible] = useState<Record<string, boolean>>({})
  const [testing, setTesting] = useState<Record<string, boolean>>({})
  const [testResult, setTestResult] = useState<Record<string, 'valid' | 'invalid' | ''>>({})

  const toggleVisibility = (provider: string) =>
    setVisible((v) => ({ ...v, [provider]: !v[provider] }))

  const testKey = async (provider: 'openai' | 'anthropic' | 'google') => {
    const key = apiKeys[provider]
    if (!key) return
    setTesting((t) => ({ ...t, [provider]: true }))
    setTestResult((r) => ({ ...r, [provider]: '' }))
    try {
      const res = await fetch('/api/settings/validate-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, key }),
      })
      const data = await res.json()
      setTestResult((r) => ({ ...r, [provider]: data.valid ? 'valid' : 'invalid' }))
    } catch {
      setTestResult((r) => ({ ...r, [provider]: 'invalid' }))
    } finally {
      setTesting((t) => ({ ...t, [provider]: false }))
    }
  }

  const maskKey = (key: string) => {
    if (!key) return ''
    if (key.length <= 8) return '****' + key.slice(-4)
    return '****' + key.slice(-4)
  }

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
            onClick={onClose}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div
              className="bg-card border rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between px-6 py-4 border-b bg-muted/30">
                <h2 className="text-sm font-bold uppercase tracking-widest text-muted-foreground">API Keys</h2>
                <button onClick={onClose} className="text-muted-foreground hover:text-foreground transition-colors">
                  <X className="size-4" />
                </button>
              </div>

              <div className="p-6 space-y-5">
                <p className="text-xs text-muted-foreground leading-relaxed">
                  Your keys are stored locally in your browser and sent per-request via headers. They are never stored server-side.
                </p>

                {PROVIDERS.map(({ key, label, placeholder }) => (
                  <div key={key} className="space-y-2">
                    <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground">{label}</label>
                    <div className="flex gap-2">
                      <div className="relative flex-1">
                        <input
                          type={visible[key] ? 'text' : 'password'}
                          value={visible[key] ? apiKeys[key] : (apiKeys[key] ? maskKey(apiKeys[key]) : '')}
                          placeholder={placeholder}
                          onChange={(e) => {
                            setApiKey(key, e.target.value)
                            setTestResult((r) => ({ ...r, [key]: '' }))
                          }}
                          onFocus={() => setVisible((v) => ({ ...v, [key]: true }))}
                          className={cn(
                            'w-full rounded-lg border bg-background px-3 py-2 text-sm font-mono',
                            'focus:outline-none focus:ring-2 focus:ring-primary/50',
                            'placeholder:text-muted-foreground/50',
                          )}
                        />
                        <button
                          onClick={() => toggleVisibility(key)}
                          className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                        >
                          {visible[key] ? <EyeOff className="size-3.5" /> : <Eye className="size-3.5" />}
                        </button>
                      </div>
                      <button
                        onClick={() => testKey(key)}
                        disabled={!apiKeys[key] || testing[key]}
                        className={cn(
                          'px-3 py-2 rounded-lg text-xs font-bold uppercase tracking-wider transition-all',
                          'border hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed',
                          testResult[key] === 'valid' && 'border-green-500 text-green-500',
                          testResult[key] === 'invalid' && 'border-red-500 text-red-500',
                        )}
                      >
                        {testing[key] ? (
                          <Loader2 className="size-3.5 animate-spin" />
                        ) : testResult[key] === 'valid' ? (
                          <CheckCircle className="size-3.5" />
                        ) : testResult[key] === 'invalid' ? (
                          <XCircle className="size-3.5" />
                        ) : (
                          'Test'
                        )}
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              <div className="px-6 py-4 border-t bg-muted/30 flex justify-between">
                <button
                  onClick={() => {
                    clearAllApiKeys()
                    setTestResult({})
                  }}
                  className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-bold uppercase tracking-wider text-red-500 hover:bg-red-500/10 transition-colors"
                >
                  <Trash2 className="size-3.5" />
                  Clear All Keys
                </button>
                <button
                  onClick={onClose}
                  className="px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wider bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
                >
                  Done
                </button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
