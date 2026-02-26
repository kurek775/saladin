import { useEffect, useRef, useMemo, useState } from 'react'
import { Terminal, Trash2, Search, Zap } from 'lucide-react'
import { useStore } from '../../store'
import { LogEntryRow } from './LogEntry'
import { cn } from '../../utils'

export function LiveLogPanel({ taskId }: { taskId?: string }) {
  const logs = useStore((s) => s.logs)
  const clearLogs = useStore((s) => s.clearLogs)
  const bottomRef = useRef<HTMLDivElement>(null)
  const [isAutoScroll, setIsAutoScroll] = useState(true)

  const filtered = useMemo(
    () => (taskId ? logs.filter((l) => l.task_id === taskId) : logs),
    [logs, taskId]
  )

  useEffect(() => {
    if (isAutoScroll) {
      const timer = setTimeout(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
      }, 100)
      return () => clearTimeout(timer)
    }
  }, [filtered.length, isAutoScroll])

  return (
    <div className="flex flex-col h-full bg-muted/40 dark:bg-[#0a0a0b] border rounded-xl overflow-hidden shadow-2xl">
      <div className="flex items-center justify-between px-4 py-2 bg-card/50 border-b backdrop-blur-sm">
        <div className="flex items-center gap-2">
          <Terminal className="size-3.5 text-primary" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Terminal Output</h3>
          <div className="flex items-center gap-1.5 ml-4">
            <span className="size-1.5 rounded-full bg-green-500 animate-pulse" />
            <span className="text-xs text-green-500/80 font-mono">LIVE</span>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-2 py-1 rounded bg-muted/30 border border-transparent focus-within:border-primary/30 transition-colors group">
            <Search className="size-3 text-muted-foreground group-focus-within:text-primary transition-colors" />
            <input 
              type="text" 
              placeholder="Filter logs..." 
              className="bg-transparent border-none outline-none text-xs w-24 focus:w-40 transition-all placeholder:text-muted-foreground/50"
            />
          </div>
          <div className="h-4 w-px bg-border" />
          <button 
            onClick={() => setIsAutoScroll(!isAutoScroll)}
            className={cn(
              "text-xs font-medium transition-colors flex items-center gap-1",
              isAutoScroll ? "text-primary" : "text-muted-foreground hover:text-foreground"
            )}
          >
            <Zap className={cn("size-3", isAutoScroll && "fill-primary/20")} />
            {isAutoScroll ? 'Auto-scroll ON' : 'Auto-scroll OFF'}
          </button>
          <button 
            onClick={clearLogs} 
            className="text-muted-foreground hover:text-destructive transition-colors"
            title="Clear logs"
          >
            <Trash2 className="size-3.5" />
          </button>
        </div>
      </div>
      
      <div className="flex-1 p-4 overflow-auto font-mono scroll-smooth selection:bg-primary/30">
        <div className="space-y-1">
          {filtered.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full py-12 opacity-30 select-none">
              <Terminal className="size-8 mb-2" />
              <p className="text-xs">No activity detected. Waiting for system events...</p>
            </div>
          ) : (
            filtered.map((log) => <LogEntryRow key={log.id} log={log} />)
          )}
          <div ref={bottomRef} className="h-4" />
        </div>
      </div>
      
      <div className="px-4 py-1.5 bg-muted/20 border-t flex items-center justify-between">
        <div className="flex items-center gap-3 text-[10px] text-muted-foreground/60 uppercase tracking-widest font-bold">
          <span>UTF-8</span>
          <span>Log Level: ALL</span>
        </div>
        <span className="text-[10px] text-muted-foreground/60 font-mono">Lines: {filtered.length}</span>
      </div>
    </div>
  )
}
