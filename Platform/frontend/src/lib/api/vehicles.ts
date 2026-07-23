import api from '@/lib/api'
import type { Vehicle, VehicleTelemetry } from '@/types'

export const vehicleApi = {
  list: () => api.get<Vehicle[]>('/api/vehicles'),
  get: (id: string) => api.get<Vehicle>(`/api/vehicles/${id}`),
  telemetry: (_id: string, _range?: string) =>
    Promise.resolve({ data: [] as VehicleTelemetry[], status: 200, statusText: 'OK', headers: {}, config: {} as any }),
}
