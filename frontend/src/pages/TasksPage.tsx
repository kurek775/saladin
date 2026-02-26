import { useMemo } from 'react'
import { motion } from 'framer-motion'
import { useTasks } from '../hooks/useTasks'
import { useStore } from '../store'
import { TaskSubmitForm } from '../components/tasks/TaskSubmitForm'
import { TaskTable } from '../components/tasks/TaskTable'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { ClipboardList, PlusCircle } from 'lucide-react'

export function TasksPage() {
  const query = useTasks()
  const tasksMap = useStore((s) => s.tasks)
  const sorted = useMemo(
    () =>
      Object.values(tasksMap).sort((a, b) => b.created_at.localeCompare(a.created_at)),
    [tasksMap]
  )

  if (query.isLoading) return <LoadingSpinner />

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8 max-w-7xl mx-auto"
    >
      <header>
        <div className="flex items-center gap-2 mb-1">
          <ClipboardList className="size-5 text-primary" />
          <h2 className="text-2xl font-bold tracking-tight">Tasks</h2>
        </div>
        <p className="text-muted-foreground text-sm">Create, manage and monitor your agentic workflows.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        <section className="lg:col-span-1 space-y-4 sticky top-24">
          <div className="flex items-center gap-2">
            <PlusCircle className="size-4 text-primary" />
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">New Task</h3>
          </div>
          <div className="bg-muted/40 border rounded-xl p-6 shadow-sm">
            <TaskSubmitForm />
          </div>
        </section>

        <section className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Task History</h3>
            <span className="text-xs bg-muted px-2 py-0.5 rounded font-bold">{sorted.length} TOTAL</span>
          </div>
          <div className="bg-card border rounded-xl shadow-sm overflow-hidden">
            <TaskTable tasks={sorted} />
          </div>
        </section>
      </div>
    </motion.div>
  )
}
