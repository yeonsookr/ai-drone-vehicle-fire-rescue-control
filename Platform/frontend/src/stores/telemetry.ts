import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { DroneTelemetry, VehicleTelemetry } from '@/types'
import { subscribeTelemetry, subscribeVehicleTelemetry } from '@/lib/api/telemetry'

const MAX_HISTORY = 300

export const useTelemetryStore = defineStore('telemetry', () => {
  // Drone telemetry
  const latest = ref<Map<string, DroneTelemetry>>(new Map())
  const history = ref<Map<string, DroneTelemetry[]>>(new Map())
  const droneIds = computed(() => [...latest.value.keys()])

  // Vehicle telemetry
  const vehicleLatest = ref<Map<string, VehicleTelemetry>>(new Map())
  const vehicleHistory = ref<Map<string, VehicleTelemetry[]>>(new Map())
  const vehicleIds = computed(() => [...vehicleLatest.value.keys()])

  const connected = ref(false)
  const version = ref(0)

  let unsubDrone: (() => void) | null = null
  let unsubVehicle: (() => void) | null = null

  function latestOf(droneId: string): DroneTelemetry | null {
    return latest.value.get(droneId) ?? null
  }

  function historyOf(droneId: string): DroneTelemetry[] {
    return history.value.get(droneId) ?? []
  }

  function vehicleLatestOf(id: string): VehicleTelemetry | null {
    return vehicleLatest.value.get(id) ?? null
  }

  function vehicleHistoryOf(id: string): VehicleTelemetry[] {
    return vehicleHistory.value.get(id) ?? []
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

  function pushVehicle(entry: VehicleTelemetry) {
    vehicleLatest.value = new Map(vehicleLatest.value).set(entry.vehicle_id, entry)
    version.value++
    connected.value = true

    const h = vehicleHistory.value.get(entry.vehicle_id) ?? []
    h.push(entry)
    if (h.length > MAX_HISTORY) h.splice(0, h.length - MAX_HISTORY)
    vehicleHistory.value = new Map(vehicleHistory.value).set(entry.vehicle_id, h)
  }

  function start() {
    if (!unsubDrone) unsubDrone = subscribeTelemetry(push)
    if (!unsubVehicle) unsubVehicle = subscribeVehicleTelemetry(pushVehicle)
  }

  function stop() {
    unsubDrone?.()
    unsubDrone = null
    unsubVehicle?.()
    unsubVehicle = null
  }

  return {
    latest, history, droneIds,
    vehicleLatest, vehicleHistory, vehicleIds,
    connected, version,
    latestOf, historyOf, vehicleLatestOf, vehicleHistoryOf,
    push, pushVehicle,
    start, stop,
  }
})
