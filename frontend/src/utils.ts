import type { TaskSummary } from './api/types'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

const ACTIVE_STATUSES = new Set(['running', 'under_review', 'revision'])

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function isActiveTask(task: TaskSummary): boolean {
  return ACTIVE_STATUSES.has(task.status)
}
