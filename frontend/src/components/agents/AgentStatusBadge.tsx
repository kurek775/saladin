import { StatusBadge } from '../common/StatusBadge'
import type { AgentStatus } from '../../api/types'

export function AgentStatusBadge({ status }: { status: AgentStatus }) {
  return <StatusBadge status={status} />
}
