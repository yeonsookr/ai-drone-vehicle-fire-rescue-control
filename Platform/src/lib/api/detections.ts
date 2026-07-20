import api from '../api'
import type { AiDetection, OperatorJudgment } from '@/types'

export const detectionApi = {
  list: (params?: { judgment?: OperatorJudgment; limit?: number }) =>
    api.get<AiDetection[]>('/api/detections', { params }),
  get: (id: string) => api.get<AiDetection>(`/api/detections/${id}`),
  judge: (id: string, judgment: OperatorJudgment, reason?: string) =>
    api.patch<AiDetection>(`/api/detections/${id}/judge`, { judgment, reason }),
}
