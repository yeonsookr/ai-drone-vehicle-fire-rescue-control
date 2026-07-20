import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { DroneTelemetry } from '@/types'
import { subscribeTelemetry } from '@/lib/api/telemetry'

const MAX_HISTORY = 300

export const useTelemetryStore = defineStore('telemetry', () => {
  const latest = ref<Map<string, DroneTelemetry>>(new Map())
  const history = ref<Map<string, DroneTelemetry[]>>(new Map())
  const connected = ref(false)

  const droneIds = computed(() => [...latest.value.keys()])
  const version = ref(0)

  let unsubscribe: (() => void) | null = null

  function latestOf(droneId: string): DroneTelemetry | null {
    return latest.value.get(droneId) ?? null
  }

  function historyOf(droneId: string): DroneTelemetry[] {
    return history.value.get(droneId) ?? []
  }

  function push(entry: DroneTelemetry) {
    latest.value = new Map(latest.value).set(entry.drone_id, entry)
    version.value++
    connected.value = true

    const h = history.value.get(entry.drone_id) ?? []
    h.push(entry)
    if (h.length > MAX_HISTORY) h.splice(0, h.length - MAX_HISTORY)
    history.value = new Map(history.value).set(entry.drone_id, h)
  }

  function start() {
    if (unsubscribe) return
    unsubscribe = subscribeTelemetry(push)
  }

  function stop() {
    unsubscribe?.()
    unsubscribe = null
  }

  return {
    latest, history, connected, droneIds, version,
    latestOf, historyOf, push,
    start, stop,
  }
})
