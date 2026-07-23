import api from '@/lib/api'
import type { Drone, DroneTelemetry } from '@/types'

export const droneApi = {
  list: () => api.get<Drone[]>('/api/drones'),
  get: (id: string) => api.get<Drone>(`/api/drones/${id}`),
  telemetry: (_id: string, _range?: string) =>
    Promise.resolve({ data: [] as DroneTelemetry[], status: 200, statusText: 'OK', headers: {}, config: {} as any }),
}
