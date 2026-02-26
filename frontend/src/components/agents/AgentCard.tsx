import { memo, useCallback } from 'react'
import type { Agent } from '../../api/types'
import { AgentStatusBadge } from './AgentStatusBadge'
import { useDeleteAgent } from '../../hooks/useAgents'
import { Trash2, Calendar, Cpu, Shield, MessageSquareText } from 'lucide-react'
import { cn } from '../../utils'

const PROVIDER_COLORS: Record<string, string> = {
  anthropic: 'bg-orange-500/10 text-orange-500 border-orange-500/20',
  openai: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
  gemini: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  ollama: 'bg-purple-500/10 text-purple-500 border-purple-500/20',
}

function ProviderBadge({ provider, model }: { provider: string; model: string }) {
  if (!provider) return (
    <span className="inline-flex items-center gap-1 text-xs font-bold px-2 py-0.5 rounded-full bg-muted text-muted-foreground border border-transparent">
      <Cpu className="size-2.5" /> GLOBAL DEFAULT
    </span>
  )
  
  const colors = PROVIDER_COLORS[provider] ?? 'bg-muted text-muted-foreground border-transparent'
  const modelPart = model ? model.split('-')[0].split('/')[0] : ''
  const label = model ? `${provider} • ${modelPart}` : provider
  
  return (
    <span className={cn(
      "inline-flex items-center gap-1 text-xs font-bold px-2 py-0.5 rounded-full border uppercase tracking-tight",
      colors
    )}>
      <Cpu className="size-2.5" /> {label}
    </span>
  )
}

export const AgentCard = memo(function AgentCard({ agent }: { agent: Agent }) {
  const deleteMutation = useDeleteAgent()

  const handleDelete = useCallback(() => {
    if (window.confirm(`Are you sure you want to delete agent "${agent.name}"?`)) {
      deleteMutation.mutate(agent.id)
    }
  }, [deleteMutation, agent.id, agent.name])

  return (
    <div className="bg-card border rounded-xl p-5 shadow-sm hover:shadow-md transition-all group flex flex-col h-full">
      <div className="flex items-start justify-between gap-4 mb-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-bold text-foreground truncate group-hover:text-primary transition-colors">
              {agent.name}
            </h3>
            <span className={cn(
              "px-1.5 py-0.5 rounded text-[11px] font-black uppercase tracking-widest",
              agent.role === 'supervisor' ? "bg-primary/20 text-primary" : "bg-muted text-muted-foreground"
            )}>
              {agent.role}
            </span>
          </div>
          <ProviderBadge provider={agent.llm_provider} model={agent.llm_model} />
        </div>
        <AgentStatusBadge status={agent.status} className="shrink-0" />
      </div>

      <div className="flex-1 space-y-3">
        {agent.system_prompt ? (
          <div className="relative">
            <MessageSquareText className="absolute left-0 top-0.5 size-3.5 text-muted-foreground/40" />
            <p className="text-xs text-muted-foreground leading-relaxed pl-5 line-clamp-3 italic">
              "{agent.system_prompt}"
            </p>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-xs text-muted-foreground/50">
            <Shield className="size-3.5" />
            <span className="italic">Standard operational profile</span>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between mt-6 pt-4 border-t border-border/50">
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground font-medium uppercase tracking-wider">
          <Calendar className="size-3 text-muted-foreground/40" />
          {new Date(agent.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
        </div>
        
        <button
          onClick={handleDelete}
          disabled={deleteMutation.isPending}
          className="p-2 rounded-lg text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-all opacity-0 group-hover:opacity-100 disabled:opacity-0"
          title="Delete Agent"
        >
          <Trash2 className="size-4" />
        </button>
      </div>
    </div>
  )
})
