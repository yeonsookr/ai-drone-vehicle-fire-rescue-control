import api from '../api'
import type { Drone, DroneTelemetry } from '@/types'

export const droneApi = {
  list: () => api.get<Drone[]>('/api/drones'),
  get: (id: string) => api.get<Drone>(`/api/drones/${id}`),
  telemetry: (id: string, range?: string) =>
    api.get<DroneTelemetry[]>(`/api/drones/${id}/telemetry`, { params: { range } }),
}
