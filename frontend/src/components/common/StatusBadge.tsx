import { memo } from 'react'
import { cn } from '../../utils'

const statusConfig: Record<string, { label: string; dot: string; bg: string; text: string }> = {
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

export const StatusBadge = memo(function StatusBadge({ status, className }: { status: string; className?: string }) {
  const config = statusConfig[status] || statusConfig.idle
  
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
