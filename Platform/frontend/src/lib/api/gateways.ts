import api from '@/lib/api'
import type { Gateway } from '@/types'

export const gatewayApi = {
  list: () => api.get<Gateway[]>('/api/gateways'),
  get: (id: string) => api.get<Gateway>(`/api/gateways/${id}`),
}
