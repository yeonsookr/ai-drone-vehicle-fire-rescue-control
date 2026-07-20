import { useTelemetryStore } from '@/stores/telemetry'

export function useTelemetryService() {
  const s = useTelemetryStore()
  return {
    get connected() { return s.connected },
    get droneIds() { return s.droneIds },
    get latest() { return s.latest },
    get version() { return s.version },
    start: () => s.start(),
    stop: () => s.stop(),
    latestOf: (id: string) => s.latestOf(id),
    historyOf: (id: string) => s.historyOf(id),
  }
}
