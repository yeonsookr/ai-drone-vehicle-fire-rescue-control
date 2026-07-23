import { ref } from 'vue'
import { streamApi } from '@/lib/api/streams'
import type { VideoStream } from '@/types'

const streams = ref<VideoStream[]>([])

export function useStreamService() {
  async function fetch() {
    const { data } = await streamApi.list()
    streams.value = data
  }
  fetch()

  return {
    get all() { return streams.value },
    get active() { return streams.value.filter(s => s.status === 'streaming' && s.device_type === 'drone') },
    ofId: (id: number) => streams.value.find(s => s.id === id) ?? null,
  }
}
