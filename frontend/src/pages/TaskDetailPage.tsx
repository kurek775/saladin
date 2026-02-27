import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useTask } from '../hooks/useTasks'
import { useStore } from '../store'
import { StatusBadge } from '../components/common/StatusBadge'
import { TaskTimeline } from '../components/tasks/TaskTimeline'
import { LiveLogPanel } from '../components/logs/LiveLogPanel'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { HumanApprovalPanel } from '../components/tasks/HumanApprovalPanel'
import { ArrowLeft, ClipboardList, CheckCircle, FileText, Activity, Clock, Hash, History, Zap, DollarSign } from 'lucide-react'

export function TaskDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: task, isLoading, refetch } = useTask(id!)
  const getTaskTelemetry = useStore((s) => s.getTaskTelemetry)
  const telemetry = id ? getTaskTelemetry(id) : null

  if (isLoading) return <LoadingSpinner />
  if (!task) {
    return (
      <div className="max-w-7xl mx-auto flex flex-col items-center justify-center py-20 text-center">
        <p className="text-destructive font-semibold mb-2">Task not found</p>
        <Link to="/tasks" className="text-sm text-primary hover:underline">Back to Tasks</Link>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className="space-y-8 max-w-7xl mx-auto"
    >
      <header className="flex flex-col gap-4">
        <Link
          to="/tasks"
          className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-muted-foreground hover:text-primary transition-colors group w-fit"
        >
          <ArrowLeft className="size-3 group-hover:-translate-x-1 transition-transform" />
          Back to Tasks
        </Link>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="size-12 rounded-xl bg-primary/10 flex items-center justify-center">
              <ClipboardList className="size-6 text-primary" />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h2 className="text-2xl font-bold tracking-tight">Task Details</h2>
                <StatusBadge status={task.status} />
              </div>
              <div className="flex items-center gap-3 text-xs text-muted-foreground font-mono uppercase tracking-tighter">
                <span className="flex items-center gap-1"><Hash className="size-2.5" /> {task.id}</span>
                <span className="flex items-center gap-1"><Clock className="size-2.5" /> Created {new Date(task.created_at).toLocaleString()}</span>
                {task.current_revision > 0 && (
                  <span className="flex items-center gap-1 text-primary font-bold"><History className="size-2.5" /> Revision {task.current_revision}</span>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          {/* Main Info */}
          <section className="bg-card border rounded-xl overflow-hidden shadow-sm">
            <div className="px-6 py-4 border-b bg-muted/30 flex items-center gap-2">
              <FileText className="size-4 text-primary" />
              <h3 className="text-xs font-bold uppercase tracking-widest text-muted-foreground">Original Request</h3>
            </div>
            <div className="p-6">
              <p className="text-base text-foreground/90 leading-relaxed font-medium">
                {task.description}
              </p>
            </div>
          </section>

          {/* Human Approval Panel */}
          {task.status === 'pending_human_approval' && (
            <HumanApprovalPanel task={task} onDecisionMade={() => refetch()} />
          )}

          {/* Final Output */}
          {task.final_output && (
            <section className="bg-card border-2 border-green-500/20 rounded-xl overflow-hidden shadow-lg shadow-green-500/5 ring-4 ring-green-500/5">
              <div className="px-6 py-4 border-b border-green-500/10 bg-green-500/5 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle className="size-4 text-green-500" />
                  <h3 className="text-xs font-bold uppercase tracking-widest text-green-600">Final Deliverable</h3>
                </div>
                <span className="text-xs font-black bg-green-500 text-white px-2 py-0.5 rounded">COMPLETED</span>
              </div>
              <div className="p-6 bg-muted/40 dark:bg-[#0a0a0b]">
                <pre className="text-sm text-foreground/90 whitespace-pre-wrap font-mono leading-relaxed max-h-[500px] overflow-auto custom-scrollbar">
                  {task.final_output}
                </pre>
              </div>
            </section>
          )}

          {/* Timeline */}
          <section className="space-y-4">
            <div className="flex items-center gap-2 px-2">
              <History className="size-4 text-primary" />
              <h3 className="text-xs font-bold uppercase tracking-widest text-muted-foreground">Orchestration Timeline</h3>
            </div>
            <div className="bg-card border rounded-xl p-6 shadow-sm">
              <TaskTimeline outputs={task.worker_outputs} reviews={task.supervisor_reviews} />
            </div>
          </section>
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          {/* Token Telemetry */}
          {telemetry && telemetry.total_tokens > 0 && (
            <section className="bg-card border rounded-xl p-5 space-y-3">
              <div className="flex items-center gap-2">
                <Zap className="size-4 text-primary" />
                <h3 className="text-xs font-bold uppercase tracking-widest text-muted-foreground">Token Usage</h3>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div className="bg-muted/30 rounded-lg p-2.5">
                  <p className="text-[10px] text-muted-foreground uppercase">Input</p>
                  <p className="text-sm font-bold font-mono">{telemetry.total_input_tokens.toLocaleString()}</p>
                </div>
                <div className="bg-muted/30 rounded-lg p-2.5">
                  <p className="text-[10px] text-muted-foreground uppercase">Output</p>
                  <p className="text-sm font-bold font-mono">{telemetry.total_output_tokens.toLocaleString()}</p>
                </div>
              </div>
              <div className="flex items-center gap-1.5 text-xs">
                <DollarSign className="size-3 text-muted-foreground" />
                <span className="text-muted-foreground">Est. cost:</span>
                <span className="font-bold font-mono">${telemetry.total_cost_usd.toFixed(4)}</span>
              </div>
            </section>
          )}

          {/* Logs */}
          <section className="h-full flex flex-col">
            <div className="flex items-center gap-2 mb-3 px-2">
              <Activity className="size-4 text-primary" />
              <h3 className="text-xs font-bold uppercase tracking-widest text-muted-foreground">Task Execution Stream</h3>
            </div>
            <div className="flex-1 min-h-[600px] sticky top-24">
              <LiveLogPanel taskId={task.id} />
            </div>
          </section>
        </div>
      </div>
    </motion.div>
  )
}
