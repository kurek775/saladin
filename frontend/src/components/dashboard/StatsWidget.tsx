import { useMemo } from 'react'
import { useStore } from '../../store'
import { isActiveTask, cn } from '../../utils'
import { Users, CheckCircle2, PlayCircle, ArrowUpRight } from 'lucide-react'

function ActivityIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
    </svg>
  )
}

function StatCard({ label, value, icon: Icon, description, trend, color }: {
  label: string
  value: number
  icon: React.ElementType
  description?: string
  trend?: string
  color?: string
}) {
  return (
    <div className="bg-card border rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
      <div className="flex justify-between items-start relative z-10">
        <div className="space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-muted-foreground">{label}</p>
          <p className={cn("text-3xl font-bold tracking-tight", color)}>{value}</p>
        </div>
        <div className="size-10 bg-muted/50 rounded-lg flex items-center justify-center text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary transition-colors">
          <Icon className="size-5" />
        </div>
      </div>
      {(description || trend) && (
        <div className="mt-4 flex items-center justify-between relative z-10">
          <p className="text-xs text-muted-foreground font-medium">{description}</p>
          {trend && (
            <span className="text-xs font-bold text-green-500 bg-green-500/10 px-1.5 py-0.5 rounded flex items-center gap-0.5">
              <ArrowUpRight className="size-2.5" />
              {trend}
            </span>
          )}
        </div>
      )}
      <div className="absolute -right-4 -bottom-4 size-24 bg-primary/5 rounded-full blur-2xl group-hover:bg-primary/10 transition-colors" />
    </div>
  )
}

export function StatsWidget() {
  const agentsMap = useStore((s) => s.agents)
  const tasksMap = useStore((s) => s.tasks)
  const agents = useMemo(() => Object.values(agentsMap), [agentsMap])
  const tasks = useMemo(() => Object.values(tasksMap), [tasksMap])
  const activeTasks = useMemo(() => tasks.filter(isActiveTask), [tasks])

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        label="Total Agents"
        value={agents.length}
        icon={Users}
        description="Registered AI workers"
        trend="+2 this week"
      />
      <StatCard
        label="Busy Agents"
        value={agents.filter((a) => a.status === 'busy').length}
        icon={PlayCircle}
        description="Currently executing tasks"
        color="text-primary"
      />
      <StatCard
        label="Active Tasks"
        value={activeTasks.length}
        icon={ActivityIcon}
        description="In progress or under review"
        color="text-amber-500"
      />
      <StatCard
        label="Total Tasks"
        value={tasks.length}
        icon={CheckCircle2}
        description="Lifetime tasks processed"
        trend="+12% from last month"
      />
    </div>
  )
}
