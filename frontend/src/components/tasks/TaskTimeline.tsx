import { useMemo } from 'react'
import type { WorkerOutput, SupervisorReview } from '../../api/types'
import { Bot, ShieldCheck, Clock, CheckCircle2, RotateCcw, AlertCircle, FileJson } from 'lucide-react'
import { cn } from '../../utils'

type TimelineEntry =
  | { kind: 'worker'; data: WorkerOutput }
  | { kind: 'review'; data: SupervisorReview }

function entryKey(entry: TimelineEntry): string {
  if (entry.kind === 'worker') {
    return `worker-${entry.data.agent_id}-${entry.data.revision}-${entry.data.timestamp}`
  }
  return `review-${entry.data.revision}-${entry.data.timestamp}`
}

export function TaskTimeline({
  outputs,
  reviews,
}: {
  outputs: WorkerOutput[]
  reviews: SupervisorReview[]
}) {
  const entries = useMemo(() => {
    const combined: TimelineEntry[] = [
      ...outputs.map((o) => ({ kind: 'worker' as const, data: o })),
      ...reviews.map((r) => ({ kind: 'review' as const, data: r })),
    ]
    return combined.sort((a, b) => a.data.timestamp.localeCompare(b.data.timestamp))
  }, [outputs, reviews])

  if (entries.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 opacity-40">
        <Clock className="size-8 mb-2" />
        <p className="text-sm font-medium">Waiting for agent activity...</p>
      </div>
    )
  }

  return (
    <div className="relative space-y-6 before:absolute before:inset-0 before:ml-5 before:-translate-x-px before:h-full before:w-0.5 before:bg-gradient-to-b before:from-primary/20 before:via-muted before:to-transparent">
      {entries.map((entry, idx) => (
        <div key={entryKey(entry)} className="relative flex items-start gap-6 group">
          {/* Icon/Dot */}
          <div className={cn(
            "flex size-10 shrink-0 items-center justify-center rounded-full border shadow-sm z-10 transition-transform group-hover:scale-110",
            entry.kind === 'worker' 
              ? "bg-primary/10 border-primary/20 text-primary" 
              : "bg-secondary border-border text-foreground"
          )}>
            {entry.kind === 'worker' ? (
              <Bot className="size-5" />
            ) : (
              <ShieldCheck className="size-5" />
            )}
          </div>

          {/* Content */}
          <div className="flex-1 pb-4">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 mb-2">
              <div className="flex items-center gap-2">
                <span className={cn(
                  "text-xs font-black uppercase tracking-widest",
                  entry.kind === 'worker' ? "text-primary" : "text-foreground"
                )}>
                  {entry.kind === 'worker' ? `WORKER: ${entry.data.agent_name}` : 'SUPERVISOR REVIEW'}
                </span>
                <span className="text-xs bg-muted px-1.5 py-0.5 rounded font-mono text-muted-foreground">
                  REV {entry.data.revision}
                </span>
              </div>
              <time className="text-xs text-muted-foreground font-medium uppercase tracking-tighter flex items-center gap-1">
                <Clock className="size-2.5" />
                {new Date(entry.data.timestamp).toLocaleTimeString()}
              </time>
            </div>

            <div className={cn(
              "rounded-xl border p-4 shadow-sm",
              entry.kind === 'worker' ? "bg-card/50" : "bg-muted/30"
            )}>
              {entry.kind === 'worker' ? (
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-xs font-bold text-muted-foreground uppercase tracking-wider">
                    <FileJson className="size-3" /> Output Payload
                  </div>
                  <pre className="whitespace-pre-wrap font-mono text-xs leading-relaxed bg-muted/40 dark:bg-[#0a0a0b] rounded-lg p-4 border border-border/50 max-h-80 overflow-auto custom-scrollbar text-foreground/90">
                    {entry.data.output}
                  </pre>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-xs font-bold text-muted-foreground uppercase tracking-wider">
                      Decision & Feedback
                    </div>
                    <DecisionBadge decision={entry.data.decision} />
                  </div>
                  <p className="text-sm text-foreground/80 leading-relaxed pl-2 border-l-2 border-primary/10 italic">
                    "{entry.data.feedback}"
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

function DecisionBadge({ decision }: { decision: string }) {
  const configs: Record<string, { icon: any; class: string; label: string }> = {
    approve: { icon: CheckCircle2, class: 'bg-green-500/10 text-green-500 border-green-500/20', label: 'APPROVED' },
    revise: { icon: RotateCcw, class: 'bg-amber-500/10 text-amber-500 border-amber-500/20', label: 'REVISE' },
    reject: { icon: AlertCircle, class: 'bg-red-500/10 text-red-500 border-red-500/20', label: 'REJECTED' },
  }

  const config = configs[decision] || configs.revise

  return (
    <span className={cn(
      "inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-black uppercase tracking-widest border",
      config.class
    )}>
      <config.icon className="size-3" />
      {config.label}
    </span>
  )
}
