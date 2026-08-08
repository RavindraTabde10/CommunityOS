/**
 * Announcement constants
 */

export const PRIORITY_LEVELS = [
  { value: 'low', label: 'Low', color: 'default' },
  { value: 'normal', label: 'Normal', color: 'info' },
  { value: 'high', label: 'High', color: 'warning' },
  { value: 'critical', label: 'Critical', color: 'error' }
]

export const PRIORITY_COLORS = {
  low: 'default',
  normal: 'info',
  high: 'warning',
  critical: 'error'
}

export const getPriorityColor = (priority) => {
  return PRIORITY_COLORS[priority] || 'info'
}

export const getPriorityLabel = (priority) => {
  const found = PRIORITY_LEVELS.find(p => p.value === priority)
  return found ? found.label : priority
}
