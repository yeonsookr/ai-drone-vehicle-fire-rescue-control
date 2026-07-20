import api from '../api'
import type { AiDetection, DetectionJudgeRequest } from '@/types'

export const detectionApi = {
  list: (params?: { judgment?: string; limit?: number }) =>
    api.get<AiDetection[]>('/api/detections', { params }),
  get: (id: string) => api.get<AiDetection>(`/api/detections/${id}`),
  judge: (id: string, req: DetectionJudgeRequest) =>
    api.patch<AiDetection>(`/api/detections/${id}/judge`, req),
}
