import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchTasks, fetchTask, createTask } from '../api/client'
import { useStore } from '../store'
import { useEffect, useRef } from 'react'
import type { TaskSummary } from '../api/types'

export function useTasks() {
  const prevDataRef = useRef<TaskSummary[] | undefined>(undefined)
  const query = useQuery({
    queryKey: ['tasks'],
    queryFn: fetchTasks,
  })

  useEffect(() => {
    if (query.data && query.data !== prevDataRef.current) {
      useStore.getState().setTasks(query.data)
      prevDataRef.current = query.data
    }
  }, [query.data])

  return query
}

export function useTask(id: string) {
  return useQuery({
    queryKey: ['tasks', id],
    queryFn: () => fetchTask(id),
    staleTime: 30_000, // WebSocket provides real-time updates
  })
}

export function useCreateTask() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: { description: string; assigned_agents?: string[] }) =>
      createTask(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['tasks'] }),
  })
}
