import { StatusBadge } from '../common/StatusBadge'
import type { AgentStatus } from '../../api/types'

export function AgentStatusBadge({ status, className }: { status: AgentStatus; className?: string }): React.JSX.Element {
  return <StatusBadge status={status} className={className} />
}
