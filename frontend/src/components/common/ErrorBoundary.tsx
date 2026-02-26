import { Component, type ReactNode } from 'react'
import { AlertCircle, RotateCcw, Home } from 'lucide-react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  handleRetry = () => {
    this.setState({ hasError: false })
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback

      return (
        <div className="min-h-[400px] flex flex-col items-center justify-center p-8 text-center animate-in fade-in zoom-in duration-300">
          <div className="size-16 rounded-full bg-destructive/10 flex items-center justify-center mb-6 shadow-xl shadow-destructive/5 ring-4 ring-destructive/5">
            <AlertCircle className="size-8 text-destructive" />
          </div>
          
          <h2 className="text-2xl font-bold tracking-tight mb-2">Something went wrong</h2>
          <p className="text-muted-foreground max-w-md mb-8 leading-relaxed">
            {this.state.error?.message || "An unexpected error occurred in the orchestration engine. Please try again or return to safety."}
          </p>
          
          <div className="flex items-center gap-4">
            <button
              onClick={this.handleRetry}
              className="flex items-center gap-2 px-6 py-2.5 bg-primary text-primary-foreground rounded-lg text-xs font-bold uppercase tracking-widest hover:bg-primary/90 transition-all shadow-lg active:scale-95"
            >
              <RotateCcw className="size-4" />
              Re-initialize
            </button>
            <a
              href="/"
              className="flex items-center gap-2 px-6 py-2.5 bg-muted text-muted-foreground rounded-lg text-xs font-bold uppercase tracking-widest hover:bg-muted/80 transition-all active:scale-95"
            >
              <Home className="size-4" />
              Abort to Base
            </a>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
