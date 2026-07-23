import type { DroneTelemetry, VehicleTelemetry } from '@/types'

type DroneCallback = (entry: DroneTelemetry) => void
type VehicleCallback = (entry: VehicleTelemetry) => void

export function subscribeTelemetry(callback: DroneCallback): () => void {
  const es = new EventSource('/api/telemetry/stream')
  es.onmessage = (e) => {
    try { callback(JSON.parse(e.data)) } catch { /* ignore */ }
  }
  es.onerror = () => { /* server unavailable */ }
  return () => es.close()
}

export function subscribeVehicleTelemetry(callback: VehicleCallback): () => void {
  const es = new EventSource('/api/telemetry/stream?type=vehicle')
  es.onmessage = (e) => {
    try { callback(JSON.parse(e.data)) } catch { /* ignore */ }
  }
  es.onerror = () => { /* server unavailable */ }
  return () => es.close()
}
