import { useStore } from '../../store'
import { DollarSign, Zap, ArrowUpRight, ArrowDownRight } from 'lucide-react'

export function TelemetryWidget() {
  const { telemetry, getTotalCost } = useStore()
  const totalCost = getTotalCost()
  const taskIds = Object.keys(telemetry)
  const totalTokens = Object.values(telemetry).reduce((s, t) => s + t.total_tokens, 0)
  const totalInput = Object.values(telemetry).reduce((s, t) => s + t.total_input_tokens, 0)
  const totalOutput = Object.values(telemetry).reduce((s, t) => s + t.total_output_tokens, 0)

  return (
    <div className="bg-card border rounded-xl p-5 space-y-4">
      <div className="flex items-center gap-2">
        <Zap className="size-4 text-primary" />
        <h3 className="text-xs font-bold uppercase tracking-widest text-muted-foreground">Token Telemetry</h3>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="bg-muted/30 rounded-lg p-3">
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
            <DollarSign className="size-3" />
            Total Cost
          </div>
          <p className="text-lg font-bold font-mono">${totalCost.toFixed(4)}</p>
        </div>
        <div className="bg-muted/30 rounded-lg p-3">
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
            <Zap className="size-3" />
            Total Tokens
          </div>
          <p className="text-lg font-bold font-mono">{totalTokens.toLocaleString()}</p>
        </div>
        <div className="bg-muted/30 rounded-lg p-3">
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
            <ArrowUpRight className="size-3" />
            Input
          </div>
          <p className="text-sm font-bold font-mono">{totalInput.toLocaleString()}</p>
        </div>
        <div className="bg-muted/30 rounded-lg p-3">
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
            <ArrowDownRight className="size-3" />
            Output
          </div>
          <p className="text-sm font-bold font-mono">{totalOutput.toLocaleString()}</p>
        </div>
      </div>

      {taskIds.length > 0 && (
        <div className="text-xs text-muted-foreground">
          Tracked across {taskIds.length} task{taskIds.length !== 1 ? 's' : ''}
        </div>
      )}
    </div>
  )
}
