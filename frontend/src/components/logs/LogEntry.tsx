import { memo } from 'react'
import type { LogEntry as LogEntryType } from '../../api/types'
import { cn } from '../../utils'

const levelColors = {
  info: 'text-green-400 font-bold',
  warning: 'text-amber-400 font-bold',
  error: 'text-red-500 font-bold bg-red-500/10 px-1 rounded-sm',
}

export const LogEntryRow = memo(function LogEntryRow({ log }: { log: LogEntryType }) {
  const timeStr = new Date(log.timestamp).toLocaleTimeString([], { 
    hour12: false, 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit',
    fractionalSecondDigits: 2 
  })

  return (
    <div className="group flex gap-3 text-xs font-mono py-1 px-2 rounded hover:bg-muted/30 transition-colors border-l-2 border-transparent hover:border-primary/20">
      <span className="text-muted-foreground/40 shrink-0 select-none">
        {timeStr}
      </span>
      <span className={cn('shrink-0 min-w-[50px] uppercase tracking-tighter', levelColors[log.level as keyof typeof levelColors] || 'text-muted-foreground')}>
        {log.level}
      </span>
      <span className="text-foreground/90 break-words leading-relaxed">
        {log.message}
      </span>
    </div>
  )
})
