import type { Vehicle, VehicleTelemetry } from '@/types'

// Mock implementation. Rewrite to use api.get() when backend is ready.

const MOCK_VEHICLES: Vehicle[] = [
  { id: 'VEH-001', gateway_id: 'ORIN-001', name: 'OrinCar Alpha', type: 'mock', status: 'moving', battery_level: 78, current_lat: 37.5680, current_lng: 126.9770, current_alt: 20, created_at: '', updated_at: '' },
  { id: 'VEH-002', gateway_id: 'ORIN-001', name: 'OrinCar Bravo', type: 'mock', status: 'idle', battery_level: 92, current_lat: 37.5530, current_lng: 126.9910, current_alt: 18, created_at: '', updated_at: '' },
  { id: 'VEH-003', gateway_id: 'ORIN-002', name: 'OrinCar Charlie', type: 'mock', status: 'moving', battery_level: 65, current_lat: 37.5750, current_lng: 126.9720, current_alt: 22, created_at: '', updated_at: '' },
]

export const vehicleApi = {
  list: () => Promise.resolve({ data: MOCK_VEHICLES, status: 200, statusText: 'OK', headers: {}, config: {} as any }),
  get: (id: string) => {
    const v = MOCK_VEHICLES.find(v => v.id === id)
    return Promise.resolve({ data: v!, status: 200, statusText: 'OK', headers: {}, config: {} as any })
  },
  telemetry: (_id: string, _range?: string) =>
    Promise.resolve({ data: [] as VehicleTelemetry[], status: 200, statusText: 'OK', headers: {}, config: {} as any }),
}
