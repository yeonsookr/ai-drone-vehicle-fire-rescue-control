import { useTelemetryStore } from '@/stores/telemetry'

export function useTelemetryService() {
  const s = useTelemetryStore()
  return {
    get connected() { return s.connected },
    get droneIds() { return s.droneIds },
    get vehicleIds() { return s.vehicleIds },
    get latest() { return s.latest },
    get vehicleLatest() { return s.vehicleLatest },
    get version() { return s.version },
    start: () => s.start(),
    stop: () => s.stop(),
    latestOf: (id: string) => s.latestOf(id),
    historyOf: (id: string) => s.historyOf(id),
    vehicleLatestOf: (id: string) => s.vehicleLatestOf(id),
    vehicleHistoryOf: (id: string) => s.vehicleHistoryOf(id),
  }
}
