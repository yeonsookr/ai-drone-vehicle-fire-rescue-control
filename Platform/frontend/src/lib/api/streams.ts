import type { VideoStream } from '@/types'

// Mock implementation. Rewrite to use api.get() when backend is ready.

const MOCK_STREAMS: VideoStream[] = [
  { id: 1, mission_id: null, device_type: 'drone', device_id: 'DRONE-001', stream_url: '', status: 'streaming', started_at: new Date().toISOString(), ended_at: null },
  { id: 2, mission_id: null, device_type: 'drone', device_id: 'DRONE-002', stream_url: '', status: 'streaming', started_at: new Date().toISOString(), ended_at: null },
  { id: 3, mission_id: null, device_type: 'vehicle', device_id: 'VEH-001', stream_url: '', status: 'streaming', started_at: new Date().toISOString(), ended_at: null },
  { id: 4, mission_id: null, device_type: 'vehicle', device_id: 'VEH-002', stream_url: '', status: 'inactive', started_at: new Date().toISOString(), ended_at: null },
]

export const streamApi = {
  list: (_mission_id?: string) => Promise.resolve({ data: MOCK_STREAMS, status: 200, statusText: 'OK', headers: {}, config: {} as any }),
}
