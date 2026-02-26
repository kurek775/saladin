import type { Agent } from '../../api/types'
import { AgentCard } from './AgentCard'
import { Bot } from 'lucide-react'

export function AgentList({ agents }: { agents: Agent[] }) {
  if (agents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 px-6 bg-card border-2 border-dashed rounded-2xl text-center">
        <div className="size-16 rounded-full bg-muted flex items-center justify-center mb-6 shadow-inner">
          <Bot className="size-8 text-muted-foreground/40" />
        </div>
        <h4 className="text-lg font-bold text-foreground mb-2">No agents deployed</h4>
        <p className="text-sm text-muted-foreground max-w-sm mb-8 leading-relaxed">
          The orchestration fleet is currently empty. Add your first specialized agent to begin processing tasks.
        </p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {agents.map((agent) => (
        <AgentCard key={agent.id} agent={agent} />
      ))}
    </div>
  )
}
