import { useMemo } from 'react'
import { useStore } from '../../store'
import { StatusBadge } from '../common/StatusBadge'
import { Users } from 'lucide-react'

export function ActiveAgentsWidget() {
  const agentsMap = useStore((s) => s.agents)
  const agents = useMemo(() => Object.values(agentsMap), [agentsMap])

  if (agents.length === 0) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-muted-foreground text-sm">No agents available.</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {agents.map((a) => (
        <div
          key={a.id}
          className="bg-muted/30 rounded-lg p-3 flex items-center gap-3 hover:bg-muted/50 transition-colors group"
        >
          <div className="size-9 rounded-full bg-muted flex items-center justify-center shrink-0 group-hover:bg-primary/10 transition-colors">
            <Users className="size-4 text-muted-foreground group-hover:text-primary transition-colors" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-semibold truncate">{a.name}</p>
            <p className="text-xs text-muted-foreground uppercase tracking-tight font-medium">{a.role || 'Agent'}</p>
          </div>
          <StatusBadge status={a.status} />
        </div>
      ))}
    </div>
  )
}
