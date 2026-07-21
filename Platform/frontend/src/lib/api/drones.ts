import type { Drone, DroneTelemetry } from '@/types'

// Mock implementation. Rewrite to use api.get() when backend is ready.

const MOCK_DRONES: Drone[] = [
  { id: 'DRONE-001', name: 'Drone Alpha', type: 'mock', status: 'flying', battery_level: 85, current_lat: 37.5665, current_lng: 126.9780, current_alt: 120, created_at: '', updated_at: '' },
  { id: 'DRONE-002', name: 'Drone Bravo', type: 'mock', status: 'flying', battery_level: 72, current_lat: 37.5512, current_lng: 126.9885, current_alt: 95, created_at: '', updated_at: '' },
  { id: 'DRONE-003', name: 'Drone Charlie', type: 'mock', status: 'flying', battery_level: 91, current_lat: 37.5789, current_lng: 126.9700, current_alt: 150, created_at: '', updated_at: '' },
  { id: 'DRONE-004', name: 'Drone Delta', type: 'mock', status: 'flying', battery_level: 64, current_lat: 37.5600, current_lng: 126.9950, current_alt: 80, created_at: '', updated_at: '' },
]

export const droneApi = {
  list: () => Promise.resolve({ data: MOCK_DRONES, status: 200, statusText: 'OK', headers: {}, config: {} as any }),
  get: (id: string) => {
    const d = MOCK_DRONES.find(d => d.id === id)
    return Promise.resolve({ data: d!, status: 200, statusText: 'OK', headers: {}, config: {} as any })
  },
  telemetry: (_id: string, _range?: string) =>
    Promise.resolve({ data: [] as DroneTelemetry[], status: 200, statusText: 'OK', headers: {}, config: {} as any }),
}
