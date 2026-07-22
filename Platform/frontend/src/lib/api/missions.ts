import type { Mission } from '@/types'

const MOCK_MISSIONS: Mission[] = [
  {
    id: 'MIS-001', type: 'patrol', status: 'IN_PROGRESS', vehicle_id: 'ORIN-001', drone_id: 'DRONE-001',
    assigned_at: '2026-07-21T09:00:00Z', started_at: '2026-07-21T09:05:00Z', completed_at: null,
    created_by: 1, created_at: '2026-07-21T08:30:00Z', updated_at: '2026-07-21T09:05:00Z',
  },
  {
    id: 'MIS-002', type: 'patrol', status: 'COMPLETED', vehicle_id: 'ORIN-001', drone_id: 'DRONE-002',
    assigned_at: '2026-07-21T08:00:00Z', started_at: '2026-07-21T08:05:00Z', completed_at: '2026-07-21T08:45:00Z',
    created_by: 1, created_at: '2026-07-21T07:30:00Z', updated_at: '2026-07-21T08:45:00Z',
  },
  {
    id: 'MIS-003', type: 'patrol', status: 'CREATED', vehicle_id: 'ORIN-002', drone_id: 'DRONE-003',
    assigned_at: null, started_at: null, completed_at: null,
    created_by: 1, created_at: '2026-07-21T10:00:00Z', updated_at: '2026-07-21T10:00:00Z',
  },
]

export const missionApi = {
  list: () => Promise.resolve({ data: MOCK_MISSIONS, status: 200, statusText: 'OK', headers: {}, config: {} as any }),
  get: (id: string) => {
    const m = MOCK_MISSIONS.find(m => m.id === id)
    return Promise.resolve({ data: m!, status: 200, statusText: 'OK', headers: {}, config: {} as any })
  },
}
