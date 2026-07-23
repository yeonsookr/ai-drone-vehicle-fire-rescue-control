import api from '@/lib/api'
import type { Command } from '@/types'

export const commandApi = {
  send: (body: { target_type: string; target_id: string; type: string; parameters?: any; expires_sec?: number }) =>
    api.post<Command>('/api/commands', body).then(r => r.data),
}
