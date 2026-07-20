import type { Gateway } from '@/types'

// Mock implementation. Rewrite to use api.get() when backend is ready.

const MOCK_GATEWAYS: Gateway[] = [
  { id: 'ORIN-001', name: 'Jetson Orin NX', status: 'online', ip_address: '192.168.1.100', last_heartbeat_at: new Date().toISOString(), created_at: '', updated_at: '' },
  { id: 'ORIN-002', name: 'Jetson Orin Nano', status: 'online', ip_address: '192.168.1.101', last_heartbeat_at: new Date().toISOString(), created_at: '', updated_at: '' },
]

export const gatewayApi = {
  list: () => Promise.resolve({ data: MOCK_GATEWAYS, status: 200, statusText: 'OK', headers: {}, config: {} as any }),
  get: (id: string) => {
    const g = MOCK_GATEWAYS.find(g => g.id === id)
    return Promise.resolve({ data: g!, status: 200, statusText: 'OK', headers: {}, config: {} as any })
  },
}
