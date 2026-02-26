import { useMemo } from 'react'
import { useStore } from '../../store'
import { StatusBadge } from '../common/StatusBadge'
import { isActiveTask } from '../../utils'

export function ActiveTasksWidget() {
  const tasksMap = useStore((s) => s.tasks)
  const activeTasks = useMemo(
    () => Object.values(tasksMap).filter(isActiveTask),
    [tasksMap],
  )

  if (activeTasks.length === 0) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-muted-foreground text-sm">No active tasks at the moment.</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {activeTasks.map((t) => (
        <div
          key={t.id}
          className="bg-muted/30 rounded-lg p-3 flex items-center justify-between hover:bg-muted/50 transition-colors cursor-pointer group"
        >
          <div className="flex flex-col gap-1 min-w-0 flex-1 mr-3">
            <span className="text-sm font-medium leading-none group-hover:text-primary transition-colors truncate">
              {t.description}
            </span>
            <span className="text-xs text-muted-foreground font-mono">ID: {t.id.slice(0, 8)}</span>
          </div>
          <StatusBadge status={t.status} />
        </div>
      ))}
    </div>
  )
}
