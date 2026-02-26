import { Loader2 } from 'lucide-react'

export function LoadingSpinner({ fullPage = false }: { fullPage?: boolean }) {
  const content = (
    <div className="flex flex-col items-center justify-center gap-3 p-12">
      <div className="relative">
        <Loader2 className="size-10 text-primary animate-spin" />
        <div className="absolute inset-0 size-10 bg-primary/20 blur-xl animate-pulse" />
      </div>
      <p className="text-xs font-bold uppercase tracking-[0.2em] text-muted-foreground animate-pulse">
        Initializing...
      </p>
    </div>
  )

  if (fullPage) {
    return (
      <div className="fixed inset-0 bg-background flex items-center justify-center z-50">
        {content}
      </div>
    )
  }

  return content
}
