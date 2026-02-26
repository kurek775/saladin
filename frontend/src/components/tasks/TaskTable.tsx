import { memo } from 'react'
import { Link } from 'react-router-dom'
import type { TaskSummary } from '../../api/types'
import { StatusBadge } from '../common/StatusBadge'
import { ExternalLink, Hash, Clock, FileText } from 'lucide-react'
import { cn } from '../../utils'

const TaskRow = memo(function TaskRow({ task }: { task: TaskSummary }) {
  return (
    <tr className="border-b transition-colors hover:bg-muted/30 group">
      <td className="py-4 px-4 max-w-md">
        <div className="flex flex-col gap-0.5">
          <span className="font-medium text-foreground group-hover:text-primary transition-colors truncate">
            {task.description}
          </span>
          <span className="text-xs text-muted-foreground font-mono flex items-center gap-1 uppercase tracking-tight">
            <Hash className="size-2.5" /> {task.id.slice(0, 8)}
          </span>
        </div>
      </td>
      <td className="py-4 px-4">
        <StatusBadge status={task.status} />
      </td>
      <td className="py-4 px-4 text-center">
        <span className="inline-flex items-center justify-center size-6 bg-muted rounded-full text-xs font-bold">
          {task.current_revision}
        </span>
      </td>
      <td className="py-4 px-4 text-muted-foreground text-xs">
        <div className="flex items-center gap-1.5 whitespace-nowrap">
          <Clock className="size-3 text-muted-foreground/50" />
          {new Date(task.created_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
        </div>
      </td>
      <td className="py-4 px-4 text-right">
        <Link
          to={`/tasks/${task.id}`}
          className="inline-flex items-center gap-1 px-3 py-1 rounded bg-secondary text-secondary-foreground text-xs font-bold uppercase tracking-wider hover:bg-primary hover:text-primary-foreground transition-all shadow-sm"
        >
          Details
          <ExternalLink className="size-3" />
        </Link>
      </td>
    </tr>
  )
})

export function TaskTable({ tasks }: { tasks: TaskSummary[] }) {
  if (tasks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-6 text-center">
        <div className="size-12 rounded-full bg-muted flex items-center justify-center mb-4">
          <FileText className="size-6 text-muted-foreground" />
        </div>
        <p className="text-sm font-medium text-foreground">No tasks found</p>
        <p className="text-xs text-muted-foreground mt-1 max-w-[200px]">Create a new task to see it listed here.</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="bg-muted/30 text-muted-foreground/60 text-left border-b border-border uppercase tracking-widest text-xs font-bold">
            <th className="py-3 px-4 font-bold">Description</th>
            <th className="py-3 px-4 font-bold">Status</th>
            <th className="py-3 px-4 font-bold text-center">Rev</th>
            <th className="py-3 px-4 font-bold">Created</th>
            <th className="py-3 px-4 font-bold text-right">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border/50">
          {tasks.map((task) => (
            <TaskRow key={task.id} task={task} />
          ))}
        </tbody>
      </table>
    </div>
  )
}
