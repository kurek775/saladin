import { GripVertical } from 'lucide-react'

interface DashboardWidgetProps {
  title: string
  children: React.ReactNode
  action?: React.ReactNode
}

export function DashboardWidget({ title, children, action }: DashboardWidgetProps) {
  return (
    <div className="flex h-full flex-col overflow-hidden rounded-xl border bg-card shadow-sm">
      <div className="flex items-center gap-2 border-b px-4 py-2.5">
        <div className="dashboard-drag-handle cursor-grab active:cursor-grabbing text-muted-foreground hover:text-foreground transition-colors p-0.5 -ml-1">
          <GripVertical className="size-4" />
        </div>
        <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex-1">
          {title}
        </h3>
        {action}
      </div>
      <div className="flex-1 overflow-auto p-4">
        {children}
      </div>
    </div>
  )
}
