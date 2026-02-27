import { ResponsiveGridLayout, useContainerWidth } from 'react-grid-layout'
import 'react-grid-layout/css/styles.css'
import { useStore } from '../store'
import { useAgents } from '../hooks/useAgents'
import { useTasks } from '../hooks/useTasks'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { LiveLogPanel } from '../components/logs/LiveLogPanel'
import { DashboardWidget } from '../components/dashboard/DashboardWidget'
import { StatsWidget } from '../components/dashboard/StatsWidget'
import { ActiveTasksWidget } from '../components/dashboard/ActiveTasksWidget'
import { ActiveAgentsWidget } from '../components/dashboard/ActiveAgentsWidget'
import { BarChart3, RotateCcw, ArrowUpRight } from 'lucide-react'

const BREAKPOINTS = { lg: 1200, md: 996, sm: 768 }
const COLS = { lg: 12, md: 12, sm: 6 }
const ROW_HEIGHT = 30

export function DashboardPage() {
  const agentsQuery = useAgents()
  const tasksQuery = useTasks()
  const dashboardLayouts = useStore((s) => s.dashboardLayouts)
  const setDashboardLayouts = useStore((s) => s.setDashboardLayouts)
  const resetDashboardLayouts = useStore((s) => s.resetDashboardLayouts)

  const { width, containerRef, mounted } = useContainerWidth()

  if (agentsQuery.isLoading || tasksQuery.isLoading) return <LoadingSpinner />
  if (agentsQuery.isError || tasksQuery.isError) {
    return (
      <div className="max-w-7xl mx-auto flex flex-col items-center justify-center py-20 text-center">
        <p className="text-destructive font-semibold mb-2">Failed to load dashboard data</p>
        <p className="text-sm text-muted-foreground mb-4">{agentsQuery.error?.message || tasksQuery.error?.message}</p>
        <button onClick={() => { agentsQuery.refetch(); tasksQuery.refetch() }} className="px-4 py-2 text-sm bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6" ref={containerRef}>
      <header className="flex items-end justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
          <p className="text-muted-foreground mt-1 text-sm">
            Real-time overview of your agent orchestration.
          </p>
        </div>
        <button
          onClick={resetDashboardLayouts}
          className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors px-3 py-1.5 rounded-md border border-transparent hover:border-border"
        >
          <RotateCcw className="size-3" />
          Reset Layout
        </button>
      </header>

      {mounted && (
        <ResponsiveGridLayout
          className="dashboard-grid"
          width={width}
          layouts={dashboardLayouts}
          breakpoints={BREAKPOINTS}
          cols={COLS}
          rowHeight={ROW_HEIGHT}
          dragConfig={{ handle: '.dashboard-drag-handle' }}
          onLayoutChange={setDashboardLayouts}
          autoSize
        >
          <div key="stats">
            <DashboardWidget title="Overview">
              <StatsWidget />
            </DashboardWidget>
          </div>

          <div key="systemActivity">
            <DashboardWidget
              title="System Activity"
              action={<BarChart3 className="size-3.5 text-primary" />}
            >
              <div className="h-full -m-4">
                <LiveLogPanel />
              </div>
            </DashboardWidget>
          </div>

          <div key="activeTasks">
            <DashboardWidget
              title="Active Tasks"
              action={
                <button className="text-xs text-primary hover:underline flex items-center gap-1">
                  View History <ArrowUpRight className="size-3" />
                </button>
              }
            >
              <ActiveTasksWidget />
            </DashboardWidget>
          </div>

          <div key="activeAgents">
            <DashboardWidget
              title="Active Agents"
              action={
                <button className="text-xs text-primary hover:underline flex items-center gap-1">
                  View All <ArrowUpRight className="size-3" />
                </button>
              }
            >
              <ActiveAgentsWidget />
            </DashboardWidget>
          </div>
        </ResponsiveGridLayout>
      )}
    </div>
  )
}
