import api from '@/lib/api'
import type { VideoStream } from '@/types'

export const streamApi = {
  list: () => api.get<VideoStream[]>('/api/video-streams'),
}
