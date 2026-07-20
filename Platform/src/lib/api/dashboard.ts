import api from '../api'
import type { DashboardSummary } from '@/types'

export const dashboardApi = {
  summary: () => api.get<DashboardSummary>('/api/dashboard/summary'),
}
