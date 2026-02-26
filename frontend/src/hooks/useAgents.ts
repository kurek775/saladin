import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchAgents, createAgent, deleteAgent, updateAgent } from '../api/client'
import type { Agent, AgentCreate } from '../api/types'
import { useStore } from '../store'
import { useEffect, useRef } from 'react'

export function useAgents() {
  const prevDataRef = useRef<Agent[] | undefined>(undefined)
  const query = useQuery({
    queryKey: ['agents'],
    queryFn: fetchAgents,
  })

  useEffect(() => {
    if (query.data && query.data !== prevDataRef.current) {
      useStore.getState().setAgents(query.data)
      prevDataRef.current = query.data
    }
  }, [query.data])

  return query
}

export function useCreateAgent() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: AgentCreate) => createAgent(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['agents'] }),
  })
}

export function useDeleteAgent() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => deleteAgent(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['agents'] }),
  })
}

export function useUpdateAgent() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<AgentCreate> }) =>
      updateAgent(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['agents'] }),
  })
}
