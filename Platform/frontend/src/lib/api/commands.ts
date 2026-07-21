import type { Command } from '@/types'

const MOCK_COMMANDS: Command[] = [
  { id: 'CMD-001', parent_command_id: null, mission_id: 'MIS-001', target_type: 'vehicle', target_id: 'ORIN-001', type: 'move', status: 'SUCCEEDED', issuer: 'operator', operator_id: 1, parameters: { lat: 37.57, lng: 126.98 }, error_reason: null, issued_at: '2026-07-21T10:00:00Z', expires_at: '2026-07-21T10:05:00Z', completed_at: '2026-07-21T10:00:30Z' },
  { id: 'CMD-002', parent_command_id: 'CMD-001', mission_id: 'MIS-001', target_type: 'drone', target_id: 'DRONE-001', type: 'move', status: 'SUCCEEDED', issuer: 'operator', operator_id: 1, parameters: { lat: 37.57, lng: 126.98, alt: 120 }, error_reason: null, issued_at: '2026-07-21T10:00:05Z', expires_at: '2026-07-21T10:00:35Z', completed_at: '2026-07-21T10:00:28Z' },
  { id: 'CMD-003', parent_command_id: null, mission_id: 'MIS-001', target_type: 'vehicle', target_id: 'ORIN-001', type: 'stop', status: 'SUCCEEDED', issuer: 'operator', operator_id: 1, parameters: {}, error_reason: null, issued_at: '2026-07-21T10:01:00Z', expires_at: '2026-07-21T10:01:30Z', completed_at: '2026-07-21T10:01:05Z' },
  { id: 'CMD-004', parent_command_id: 'CMD-003', mission_id: 'MIS-001', target_type: 'drone', target_id: 'DRONE-001', type: 'stop', status: 'FAILED', issuer: 'edge_ai', operator_id: null, parameters: {}, error_reason: 'Communication timeout', issued_at: '2026-07-21T10:01:02Z', expires_at: '2026-07-21T10:01:32Z', completed_at: '2026-07-21T10:01:10Z' },
]

export const commandApi = {
  list: (mission_id?: string) => {
    let data = [...MOCK_COMMANDS]
    if (mission_id) data = data.filter(c => c.mission_id === mission_id)
    return Promise.resolve({ data, status: 200, statusText: 'OK', headers: {}, config: {} as any })
  },
  get: (id: string) => {
    const c = MOCK_COMMANDS.find(c => c.id === id)
    return Promise.resolve({ data: c!, status: 200, statusText: 'OK', headers: {}, config: {} as any })
  },
}
