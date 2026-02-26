import type { StateCreator } from 'zustand'
import type { TaskSummary, TaskStatus } from '../api/types'

export interface TaskSlice {
  tasks: Record<string, TaskSummary>
  setTasks: (tasks: TaskSummary[]) => void
  upsertTask: (task: TaskSummary) => void
  updateTaskStatus: (id: string, status: TaskStatus) => void
}

export const createTaskSlice: StateCreator<TaskSlice> = (set) => ({
  tasks: {},
  setTasks: (tasks) =>
    set({ tasks: Object.fromEntries(tasks.map((t) => [t.id, t])) }),
  upsertTask: (task) =>
    set((s) => ({ tasks: { ...s.tasks, [task.id]: task } })),
  updateTaskStatus: (id, status) =>
    set((s) => {
      const task = s.tasks[id]
      if (!task) return s
      return { tasks: { ...s.tasks, [id]: { ...task, status } } }
    }),
})
