import { useMemo } from 'react'
import { motion } from 'framer-motion'
import { useStore } from '../store'
import { useAgents } from '../hooks/useAgents'
import { useTasks } from '../hooks/useTasks'
import { StatusBadge } from '../components/common/StatusBadge'
import { LiveLogPanel } from '../components/logs/LiveLogPanel'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { isActiveTask, cn } from '../utils'
import { Users, CheckCircle2, PlayCircle, BarChart3, ArrowUpRight } from 'lucide-react'

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
}

const item = {
  hidden: { y: 20, opacity: 0 },
  show: { y: 0, opacity: 1 }
}

export function DashboardPage() {
  const agentsQuery = useAgents()
  const tasksQuery = useTasks()
  const agentsMap = useStore((s) => s.agents)
  const tasksMap = useStore((s) => s.tasks)
  const agents = useMemo(() => Object.values(agentsMap), [agentsMap])
  const tasks = useMemo(() => Object.values(tasksMap), [tasksMap])
  const activeTasks = useMemo(() => tasks.filter(isActiveTask), [tasks])

  if (agentsQuery.isLoading || tasksQuery.isLoading) return <LoadingSpinner />

  return (
    <motion.div 
      variants={container}
      initial="hidden"
      animate="show"
      className="space-y-8 max-w-7xl mx-auto"
    >
      <header className="flex items-end justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
          <p className="text-muted-foreground mt-1 text-sm">Real-time overview of your agent orchestration.</p>
        </div>
      </header>

      {/* Stats */}
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

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* System Activity + Active Tasks — main area */}
        <div className="lg:col-span-2 space-y-6">
          <section>
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="size-4 text-primary" />
              <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">System Activity</h3>
            </div>
            <div className="h-[400px] overflow-hidden rounded-xl border bg-card shadow-sm">
              <LiveLogPanel />
            </div>
          </section>

          <section>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Active Tasks</h3>
              <button className="text-xs text-primary hover:underline flex items-center gap-1">
                View History <ArrowUpRight className="size-3" />
              </button>
            </div>

            {activeTasks.length === 0 ? (
              <div className="bg-card border rounded-xl p-8 text-center border-dashed">
                <p className="text-muted-foreground text-sm">No active tasks at the moment.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {activeTasks.map((t) => (
                  <motion.div
                    key={t.id}
                    variants={item}
                    className="bg-card border rounded-xl p-4 flex items-center justify-between shadow-sm hover:bg-muted/30 transition-colors cursor-pointer group"
                  >
                    <div className="flex flex-col gap-1 max-w-lg">
                      <span className="text-sm font-medium leading-none group-hover:text-primary transition-colors truncate">
                        {t.description}
                      </span>
                      <span className="text-xs text-muted-foreground font-mono">ID: {t.id.slice(0, 8)}</span>
                    </div>
                    <StatusBadge status={t.status} />
                  </motion.div>
                ))}
              </div>
            )}
          </section>
        </div>

        {/* Active Agents — sidebar */}
        <div className="lg:col-span-1 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Active Agents</h3>
            <button className="text-xs text-primary hover:underline flex items-center gap-1">
              View All <ArrowUpRight className="size-3" />
            </button>
          </div>

          {agents.length === 0 ? (
            <div className="bg-card border rounded-xl p-8 text-center border-dashed">
              <p className="text-muted-foreground text-sm">No agents available.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {agents.map((a) => (
                <motion.div
                  key={a.id}
                  variants={item}
                  className="bg-card border rounded-xl p-4 flex items-center gap-3 shadow-sm hover:shadow-md transition-shadow group"
                >
                  <div className="size-9 rounded-full bg-muted flex items-center justify-center shrink-0 group-hover:bg-primary/10 transition-colors">
                    <Users className="size-4 text-muted-foreground group-hover:text-primary transition-colors" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-semibold truncate">{a.name}</p>
                    <p className="text-xs text-muted-foreground uppercase tracking-tight font-medium">{a.role || 'Agent'}</p>
                  </div>
                  <StatusBadge status={a.status} />
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}

function StatCard({ label, value, icon: Icon, description, trend, color }: { 
  label: string; 
  value: number; 
  icon: any; 
  description?: string;
  trend?: string;
  color?: string;
}) {
  return (
    <motion.div 
      variants={item}
      className="bg-card border rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group"
    >
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
    </motion.div>
  )
}

function ActivityIcon(props: any) {
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
