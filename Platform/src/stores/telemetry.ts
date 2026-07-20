import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { DroneTelemetry } from '@/types'

const MAX_HISTORY = 300

export const useTelemetryStore = defineStore('telemetry', () => {
  const latest = ref<Map<string, DroneTelemetry>>(new Map())
  const history = ref<Map<string, DroneTelemetry[]>>(new Map())
  const sseConnected = ref(false)

  const droneIds = computed(() => [...latest.value.keys()])

  function latestOf(droneId: string): DroneTelemetry | null {
    return latest.value.get(droneId) ?? null
  }

  function historyOf(droneId: string): DroneTelemetry[] {
    return history.value.get(droneId) ?? []
  }

  function push(entry: DroneTelemetry) {
    latest.value.set(entry.drone_id, entry)

    const h = history.value.get(entry.drone_id) ?? []
    h.push(entry)
    if (h.length > MAX_HISTORY) h.splice(0, h.length - MAX_HISTORY)
    history.value.set(entry.drone_id, h)
  }

  function setSseConnected(v: boolean) {
    sseConnected.value = v
  }

  return {
    latest, history, sseConnected, droneIds,
    latestOf, historyOf, push, setSseConnected,
  }
})
