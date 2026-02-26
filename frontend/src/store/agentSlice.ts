import type { StateCreator } from 'zustand'
import type { Agent, AgentStatus } from '../api/types'

export interface AgentSlice {
  agents: Record<string, Agent>
  setAgents: (agents: Agent[]) => void
  upsertAgent: (agent: Agent) => void
  removeAgent: (id: string) => void
  updateAgentStatus: (id: string, status: AgentStatus) => void
}

export const createAgentSlice: StateCreator<AgentSlice> = (set) => ({
  agents: {},
  setAgents: (agents) =>
    set({ agents: Object.fromEntries(agents.map((a) => [a.id, a])) }),
  upsertAgent: (agent) =>
    set((s) => ({ agents: { ...s.agents, [agent.id]: agent } })),
  removeAgent: (id) =>
    set((s) => {
      const { [id]: _, ...rest } = s.agents
      return { agents: rest }
    }),
  updateAgentStatus: (id, status) =>
    set((s) => {
      const agent = s.agents[id]
      if (!agent) return s
      return { agents: { ...s.agents, [id]: { ...agent, status } } }
    }),
})
