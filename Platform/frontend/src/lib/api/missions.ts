import type { Mission, MissionLog } from '@/types'

const MOCK_MISSIONS: Mission[] = [
  {
    id: 'MIS-001', type: 'patrol', status: 'IN_PROGRESS', vehicle_id: 'ORIN-001', drone_id: 'DRONE-001',
    assigned_at: '2026-07-21T09:00:00Z', started_at: '2026-07-21T09:05:00Z', completed_at: null,
    created_by: 1, created_at: '2026-07-21T08:30:00Z', updated_at: '2026-07-21T09:05:00Z',
    failure_reason: null,
  },
  {
    id: 'MIS-002', type: 'patrol', status: 'COMPLETED', vehicle_id: 'ORIN-001', drone_id: 'DRONE-002',
    assigned_at: '2026-07-21T08:00:00Z', started_at: '2026-07-21T08:05:00Z', completed_at: '2026-07-21T08:45:00Z',
    created_by: 1, created_at: '2026-07-21T07:30:00Z', updated_at: '2026-07-21T08:45:00Z',
    failure_reason: null,
  },
  {
    id: 'MIS-003', type: 'patrol', status: 'CREATED', vehicle_id: 'ORIN-002', drone_id: 'DRONE-003',
    assigned_at: null, started_at: null, completed_at: null,
    created_by: 1, created_at: '2026-07-21T10:00:00Z', updated_at: '2026-07-21T10:00:00Z',
    failure_reason: null,
  },
  {
    id: 'MIS-004', type: 'fire_response', status: 'FAILED', vehicle_id: 'ORIN-001', drone_id: 'DRONE-002',
    assigned_at: '2026-07-21T11:00:00Z', started_at: '2026-07-21T11:05:00Z', completed_at: '2026-07-21T11:12:00Z',
    created_by: 1, created_at: '2026-07-21T10:50:00Z', updated_at: '2026-07-21T11:12:00Z',
    failure_reason: 'Drone communication timeout during deployment. Vehicle relay signal lost for 30s.',
  },
]

const MOCK_LOGS: Record<string, MissionLog[]> = {
  'MIS-001': [
    { id: 1, mission_id: 'MIS-001', status_from: 'CREATED', status_to: 'ASSIGNED', reason: null, changed_by: 'operator', user_id: 1, created_at: '2026-07-21T09:00:00Z' },
    { id: 2, mission_id: 'MIS-001', status_from: 'ASSIGNED', status_to: 'DISPATCHED', reason: null, changed_by: 'operator', user_id: 1, created_at: '2026-07-21T09:02:00Z' },
    { id: 3, mission_id: 'MIS-001', status_from: 'DISPATCHED', status_to: 'IN_PROGRESS', reason: null, changed_by: 'edge_ai', user_id: null, created_at: '2026-07-21T09:05:00Z' },
  ],
  'MIS-004': [
    { id: 4, mission_id: 'MIS-004', status_from: 'CREATED', status_to: 'ASSIGNED', reason: null, changed_by: 'operator', user_id: 1, created_at: '2026-07-21T11:00:00Z' },
    { id: 5, mission_id: 'MIS-004', status_from: 'ASSIGNED', status_to: 'DISPATCHED', reason: null, changed_by: 'operator', user_id: 1, created_at: '2026-07-21T11:02:00Z' },
    { id: 6, mission_id: 'MIS-004', status_from: 'DISPATCHED', status_to: 'IN_PROGRESS', reason: null, changed_by: 'edge_ai', user_id: null, created_at: '2026-07-21T11:05:00Z' },
    { id: 7, mission_id: 'MIS-004', status_from: 'IN_PROGRESS', status_to: 'FAILED', reason: 'Drone communication timeout during deployment. Vehicle relay signal lost for 30s.', changed_by: 'safety_policy', user_id: null, created_at: '2026-07-21T11:12:00Z' },
  ],
}

function clone<T>(v: T): T {
  return JSON.parse(JSON.stringify(v))
}

function findIdx(id: string): number {
  const idx = MOCK_MISSIONS.findIndex(m => m.id === id)
  if (idx === -1) throw new Error(`Mission ${id} not found`)
  return idx
}

function updateTimestamps(m: Mission): Mission {
  m.updated_at = new Date().toISOString()
  return m
}

function pushLog(mid: string, from: string, to: string, reason: string | null, by: MissionLog['changed_by']) {
  if (!MOCK_LOGS[mid]) MOCK_LOGS[mid] = []
  const id = Object.values(MOCK_LOGS).flat().length + 1
  MOCK_LOGS[mid].push({
    id, mission_id: mid, status_from: from, status_to: to, reason,
    changed_by: by, user_id: by === 'operator' ? 1 : null,
    created_at: new Date().toISOString(),
  })
}

export const missionApi = {
  list: () => Promise.resolve({ data: MOCK_MISSIONS, status: 200, statusText: 'OK', headers: {}, config: {} as any }),
  get: (id: string) => {
    const m = MOCK_MISSIONS.find(m => m.id === id)
    return Promise.resolve({ data: m!, status: 200, statusText: 'OK', headers: {}, config: {} as any })
  },

  start: (id: string) => {
    const idx = findIdx(id)
    const m = MOCK_MISSIONS[idx]
    if (m.status !== 'CREATED') return Promise.reject(new Error(`Cannot start mission in ${m.status} state`))
    const prev = m.status
    m.status = 'IN_PROGRESS'
    m.started_at = new Date().toISOString()
    m.failure_reason = null
    updateTimestamps(m)
    pushLog(id, prev, 'IN_PROGRESS', null, 'operator')
    return Promise.resolve({ data: clone(m), status: 200, statusText: 'OK', headers: {}, config: {} as any })
  },

  pause: (id: string) => {
    const idx = findIdx(id)
    const m = MOCK_MISSIONS[idx]
    if (m.status !== 'IN_PROGRESS') return Promise.reject(new Error(`Cannot pause mission in ${m.status} state`))
    const prev = m.status
    m.status = 'PAUSED'
    updateTimestamps(m)
    pushLog(id, prev, 'PAUSED', null, 'operator')
    return Promise.resolve({ data: clone(m), status: 200, statusText: 'OK', headers: {}, config: {} as any })
  },

  resume: (id: string) => {
    const idx = findIdx(id)
    const m = MOCK_MISSIONS[idx]
    if (m.status !== 'PAUSED') return Promise.reject(new Error(`Cannot resume mission in ${m.status} state`))
    const prev = m.status
    m.status = 'IN_PROGRESS'
    updateTimestamps(m)
    pushLog(id, prev, 'IN_PROGRESS', null, 'operator')
    return Promise.resolve({ data: clone(m), status: 200, statusText: 'OK', headers: {}, config: {} as any })
  },

  cancel: (id: string) => {
    const idx = findIdx(id)
    const m = MOCK_MISSIONS[idx]
    if (!['CREATED', 'IN_PROGRESS', 'PAUSED'].includes(m.status)) return Promise.reject(new Error(`Cannot cancel mission in ${m.status} state`))
    const prev = m.status
    m.status = 'CANCELLED'
    m.completed_at = new Date().toISOString()
    updateTimestamps(m)
    pushLog(id, prev, 'CANCELLED', 'Cancelled by operator', 'operator')
    return Promise.resolve({ data: clone(m), status: 200, statusText: 'OK', headers: {}, config: {} as any })
  },

  logs: (id: string) => {
    const logs = MOCK_LOGS[id] ?? []
    return Promise.resolve({ data: logs, status: 200, statusText: 'OK', headers: {}, config: {} as any })
  },
}
