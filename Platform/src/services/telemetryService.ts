import { useTelemetryStore } from '@/stores/telemetry'

export function startTelemetry() {
  useTelemetryStore().start()
}

export function stopTelemetry() {
  useTelemetryStore().stop()
}
