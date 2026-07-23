import api from '@/lib/api'
import type { Mission } from '@/types'

export const missionApi = {
  list: () => api.get<Mission[]>('/api/missions'),
}
