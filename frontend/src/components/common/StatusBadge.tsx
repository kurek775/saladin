import { memo } from 'react'
import type { AgentStatus, TaskStatus } from '../../api/types'
import { cn } from '../../utils'

type StatusKey = AgentStatus | TaskStatus

interface StatusConfig {
  label: string
  dot: string
  bg: string
  text: string
}

const statusConfig: Record<StatusKey, StatusConfig> = {
  idle: { label: 'Idle', dot: 'bg-muted-foreground', bg: 'bg-muted/50', text: 'text-muted-foreground' },
  busy: { label: 'Busy', dot: 'bg-amber-500', bg: 'bg-amber-500/10', text: 'text-amber-500' },
  error: { label: 'Error', dot: 'bg-red-500', bg: 'bg-red-500/10', text: 'text-red-500' },
  pending: { label: 'Pending', dot: 'bg-blue-400', bg: 'bg-blue-400/10', text: 'text-blue-400' },
  running: { label: 'Running', dot: 'bg-green-500', bg: 'bg-green-500/10', text: 'text-green-500' },
  under_review: { label: 'Reviewing', dot: 'bg-purple-500', bg: 'bg-purple-500/10', text: 'text-purple-500' },
  revision: { label: 'Revision', dot: 'bg-orange-500', bg: 'bg-orange-500/10', text: 'text-orange-500' },
  approved: { label: 'Approved', dot: 'bg-green-500', bg: 'bg-green-500/10', text: 'text-green-500' },
  rejected: { label: 'Rejected', dot: 'bg-red-500', bg: 'bg-red-500/10', text: 'text-red-500' },
  failed: { label: 'Failed', dot: 'bg-red-600', bg: 'bg-red-600/10', text: 'text-red-600' },
}

const FALLBACK: StatusConfig = statusConfig.idle

export const StatusBadge = memo(function StatusBadge({ status, className }: { status: StatusKey; className?: string }): React.JSX.Element {
  const config = statusConfig[status] ?? FALLBACK

  return (
    <span className={cn(
      "inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-bold uppercase tracking-wider",
      config.bg,
      config.text,
      className
    )}>
      <span className={cn("size-1.5 rounded-full", config.dot)} />
      {config.label}
    </span>
  )
})
