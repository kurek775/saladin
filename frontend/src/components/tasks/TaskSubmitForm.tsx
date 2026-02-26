import { useState } from 'react'
import { Send, Loader2, Sparkles } from 'lucide-react'
import { useCreateTask } from '../../hooks/useTasks'
import { cn } from '../../utils'

export function TaskSubmitForm() {
  const [description, setDescription] = useState('')
  const mutation = useCreateTask()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!description.trim() || mutation.isPending) return
    mutation.mutate({ description: description.trim() })
    setDescription('')
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3 group">
      <div className="relative">
        <textarea
          rows={3}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="What would you like the agents to do?"
          className="w-full bg-secondary border border-muted-foreground/20 rounded-xl px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all resize-none"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              handleSubmit(e)
            }
          }}
        />
        <div className="absolute right-3 bottom-3 flex items-center gap-2">
          <span className="text-xs text-muted-foreground/50 font-medium hidden sm:block">
            Press <kbd className="bg-muted px-1 rounded border shadow-sm">Enter</kbd> to send
          </span>
        </div>
      </div>
      
      <button
        type="submit"
        disabled={mutation.isPending || !description.trim()}
        className={cn(
          "w-full h-10 flex items-center justify-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-bold uppercase tracking-wider transition-all shadow-md active:scale-[0.98]",
          "hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100"
        )}
      >
        {mutation.isPending ? (
          <>
            <Loader2 className="size-4 animate-spin" />
            <span>Processing...</span>
          </>
        ) : (
          <>
            <Send className="size-3.5" />
            <span>Submit Task</span>
          </>
        )}
      </button>
      
      {mutation.isSuccess && (
        <p className="text-xs text-green-500 font-medium flex items-center gap-1.5 animate-in fade-in slide-in-from-top-1 duration-300">
          <Sparkles className="size-3" />
          Task created successfully!
        </p>
      )}
    </form>
  )
}
