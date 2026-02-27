import { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAgents, useCreateAgent } from '../hooks/useAgents'
import { useStore } from '../store'
import { AgentList } from '../components/agents/AgentList'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import type { AgentRole, LLMProvider } from '../api/types'
import { Bot, Plus, X, Cpu, Globe, MessageSquare, ShieldCheck } from 'lucide-react'
import { cn } from '../utils'

const PROVIDER_MODELS: Record<string, string[]> = {
  '': [],
  anthropic: ['claude-sonnet-4-20250514', 'claude-haiku-4-20250414'],
  openai: ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'o3-mini'],
  gemini: ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-2.0-flash'],
  ollama: ['llama3', 'mistral', 'codellama', 'mixtral'],
}

export function AgentsPage() {
  const query = useAgents()
  const agentsMap = useStore((s) => s.agents)
  const agents = useMemo(() => Object.values(agentsMap), [agentsMap])
  const createMutation = useCreateAgent()
  const [showForm, setShowForm] = useState(false)
  
  const [name, setName] = useState('')
  const [role, setRole] = useState<AgentRole>('worker')
  const [systemPrompt, setSystemPrompt] = useState('')
  const [llmProvider, setLlmProvider] = useState<LLMProvider>('')
  const [llmModel, setLlmModel] = useState('')

  if (query.isLoading) return <LoadingSpinner />
  if (query.isError) {
    return (
      <div className="max-w-7xl mx-auto flex flex-col items-center justify-center py-20 text-center">
        <p className="text-destructive font-semibold mb-2">Failed to load agents</p>
        <p className="text-sm text-muted-foreground mb-4">{query.error?.message}</p>
        <button onClick={() => query.refetch()} className="px-4 py-2 text-sm bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
          Retry
        </button>
      </div>
    )
  }

  const handleProviderChange = (provider: LLMProvider) => {
    setLlmProvider(provider)
    setLlmModel('')
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return
    createMutation.mutate(
      {
        name: name.trim(),
        role,
        system_prompt: systemPrompt.trim(),
        llm_provider: llmProvider,
        llm_model: llmModel,
      },
      {
        onSuccess: () => {
          setName('')
          setSystemPrompt('')
          setLlmProvider('')
          setLlmModel('')
          setShowForm(false)
        },
      }
    )
  }

  const modelOptions = PROVIDER_MODELS[llmProvider] ?? []

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8 max-w-7xl mx-auto"
    >
      <header className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Bot className="size-5 text-primary" />
            <h2 className="text-2xl font-bold tracking-tight">Agents</h2>
          </div>
          <p className="text-muted-foreground text-sm">Deploy and configure specialized AI agents.</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className={cn(
            "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-bold uppercase tracking-wider transition-all shadow-md active:scale-95",
            showForm 
              ? "bg-secondary text-secondary-foreground hover:bg-secondary/80" 
              : "bg-primary text-primary-foreground hover:bg-primary/90"
          )}
        >
          {showForm ? (
            <><X className="size-4" /> Cancel</>
          ) : (
            <><Plus className="size-4" /> New Agent</>
          )}
        </button>
      </header>

      <AnimatePresence>
        {showForm && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <form onSubmit={handleSubmit} className="bg-card border rounded-xl p-6 shadow-lg space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <label className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-muted-foreground mb-1.5">
                      <Bot className="size-3" /> Agent Name
                    </label>
                    <input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="w-full bg-muted/30 border border-input rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                      placeholder="e.g. Research Specialist"
                    />
                  </div>
                  
                  <div>
                    <label className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-muted-foreground mb-1.5">
                      <ShieldCheck className="size-3" /> Role Configuration
                    </label>
                    <div className="grid grid-cols-2 gap-2">
                      {(['worker', 'supervisor'] as const).map((r) => (
                        <button
                          key={r}
                          type="button"
                          onClick={() => setRole(r)}
                          className={cn(
                            "px-3 py-2 rounded-lg text-xs font-semibold capitalize border transition-all",
                            role === r 
                              ? "bg-primary/10 border-primary text-primary shadow-sm" 
                              : "bg-muted/30 border-transparent text-muted-foreground hover:border-input"
                          )}
                        >
                          {r}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-muted-foreground mb-1.5">
                        <Globe className="size-3" /> Provider
                      </label>
                      <select
                        value={llmProvider}
                        onChange={(e) => handleProviderChange(e.target.value as LLMProvider)}
                        className="w-full bg-muted/30 border border-input rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all appearance-none"
                      >
                        <option value="">Default (Global)</option>
                        <option value="anthropic">Anthropic</option>
                        <option value="openai">OpenAI</option>
                        <option value="gemini">Google Gemini</option>
                        <option value="ollama">Ollama (Local)</option>
                      </select>
                    </div>
                    <div>
                      <label className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-muted-foreground mb-1.5">
                        <Cpu className="size-3" /> Intelligence Model
                      </label>
                      {modelOptions.length > 0 ? (
                        <select
                          value={llmModel}
                          onChange={(e) => setLlmModel(e.target.value)}
                          className="w-full bg-muted/30 border border-input rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all appearance-none"
                        >
                          <option value="">Default Model</option>
                          {modelOptions.map((m) => (
                            <option key={m} value={m}>{m}</option>
                          ))}
                        </select>
                      ) : (
                        <input
                          type="text"
                          value={llmModel}
                          onChange={(e) => setLlmModel(e.target.value)}
                          className="w-full bg-muted/30 border border-input rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all disabled:opacity-50"
                          placeholder={llmProvider ? 'Enter model name' : 'Select provider...'}
                          disabled={!llmProvider}
                        />
                      )}
                    </div>
                  </div>

                  <div>
                    <label className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-muted-foreground mb-1.5">
                      <MessageSquare className="size-3" /> System Persona
                    </label>
                    <textarea
                      value={systemPrompt}
                      onChange={(e) => setSystemPrompt(e.target.value)}
                      rows={2}
                      className="w-full bg-muted/30 border border-input rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all resize-none"
                      placeholder="Define the agent's behavior and constraints..."
                    />
                  </div>
                </div>
              </div>

              <div className="flex justify-end pt-2 border-t">
                <button
                  type="submit"
                  disabled={createMutation.isPending || !name.trim()}
                  className="flex items-center gap-2 px-6 py-2.5 bg-primary text-primary-foreground rounded-lg text-xs font-bold uppercase tracking-widest hover:bg-primary/90 disabled:opacity-50 transition-all shadow-lg active:scale-95"
                >
                  {createMutation.isPending ? 'Deploying...' : 'Deploy Agent'}
                </button>
              </div>
            </form>
          </motion.div>
        )}
      </AnimatePresence>

      <section>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Deployed Fleet</h3>
          <span className="text-xs bg-muted px-2 py-0.5 rounded font-bold">{agents.length} ACTIVE</span>
        </div>
        <AgentList agents={agents} />
      </section>
    </motion.div>
  )
}
