import { useState } from 'react'
import { motion } from 'framer-motion'
import { ShieldCheck, ShieldX, RefreshCw, MessageSquare, Loader2 } from 'lucide-react'
import { approveTask } from '../../api/client'
import { cn } from '../../utils'
import type { Task } from '../../api/types'

interface Props {
  task: Task
  onDecisionMade?: () => void
}

export function HumanApprovalPanel({ task, onDecisionMade }: Props) {
  const [feedback, setFeedback] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  // Get the latest supervisor review
  const latestReview = task.supervisor_reviews[task.supervisor_reviews.length - 1]

  const handleDecision = async (decision: 'approve' | 'reject' | 'revise') => {
    setSubmitting(true)
    setError('')
    try {
      await approveTask(task.id, { decision, feedback })
      onDecisionMade?.()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to submit decision')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <motion.section
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card border-2 border-amber-500/30 rounded-xl overflow-hidden shadow-lg ring-4 ring-amber-500/5"
    >
      <div className="px-6 py-4 border-b border-amber-500/10 bg-amber-500/5 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldCheck className="size-4 text-amber-500" />
          <h3 className="text-xs font-bold uppercase tracking-widest text-amber-600">Human Approval Required</h3>
        </div>
        <span className="text-xs font-black bg-amber-500 text-white px-2 py-0.5 rounded">PENDING</span>
      </div>

      <div className="p-6 space-y-4">
        {latestReview && (
          <div className="bg-muted/40 rounded-lg p-4 space-y-2">
            <p className="text-xs font-bold uppercase tracking-widest text-muted-foreground">Supervisor Recommendation</p>
            <div className="flex items-center gap-2">
              <span className={cn(
                'text-xs font-bold uppercase px-2 py-0.5 rounded',
                latestReview.decision === 'approve' && 'bg-green-500/10 text-green-500',
                latestReview.decision === 'reject' && 'bg-red-500/10 text-red-500',
                latestReview.decision === 'revise' && 'bg-amber-500/10 text-amber-500',
              )}>
                {latestReview.decision}
              </span>
            </div>
            {latestReview.feedback && (
              <p className="text-sm text-foreground/80 leading-relaxed">{latestReview.feedback}</p>
            )}
          </div>
        )}

        <div className="space-y-2">
          <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground flex items-center gap-1.5">
            <MessageSquare className="size-3" />
            Your Feedback (optional)
          </label>
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Add feedback or override instructions..."
            className="w-full rounded-lg border bg-background px-3 py-2 text-sm min-h-[80px] focus:outline-none focus:ring-2 focus:ring-primary/50 placeholder:text-muted-foreground/50"
          />
        </div>

        {error && (
          <p className="text-xs text-red-500 font-medium">{error}</p>
        )}

        <div className="flex gap-3">
          <button
            onClick={() => handleDecision('approve')}
            disabled={submitting}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-bold uppercase tracking-wider bg-green-500 text-white hover:bg-green-600 transition-colors disabled:opacity-50"
          >
            {submitting ? <Loader2 className="size-3.5 animate-spin" /> : <ShieldCheck className="size-3.5" />}
            Approve
          </button>
          <button
            onClick={() => handleDecision('revise')}
            disabled={submitting}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-bold uppercase tracking-wider border border-amber-500 text-amber-500 hover:bg-amber-500/10 transition-colors disabled:opacity-50"
          >
            <RefreshCw className="size-3.5" />
            Request Revision
          </button>
          <button
            onClick={() => handleDecision('reject')}
            disabled={submitting}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-bold uppercase tracking-wider border border-red-500 text-red-500 hover:bg-red-500/10 transition-colors disabled:opacity-50"
          >
            <ShieldX className="size-3.5" />
            Reject
          </button>
        </div>
      </div>
    </motion.section>
  )
}
