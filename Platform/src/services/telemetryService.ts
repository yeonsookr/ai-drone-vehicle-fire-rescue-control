import { useTelemetryStore } from '@/stores/telemetry'

let _store: ReturnType<typeof useTelemetryStore> | null = null
function store() {
  if (!_store) _store = useTelemetryStore()
  return _store
}

export function useTelemetryService() {
  const s = store()
  return {
    connected: s.connected,
    droneIds: s.droneIds,
    latest: s.latest,
    version: s.version,
    start: () => s.start(),
    stop: () => s.stop(),
    latestOf: (id: string) => s.latestOf(id),
    historyOf: (id: string) => s.historyOf(id),
  }
}
