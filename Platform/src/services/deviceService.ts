import { useDeviceStore } from '@/stores/device'
import { useTelemetryStore } from '@/stores/telemetry'
import { computed, reactive } from 'vue'

let _deviceStore: ReturnType<typeof useDeviceStore> | null = null
let _telemetryStore: ReturnType<typeof useTelemetryStore> | null = null

function dstore() {
  if (!_deviceStore) _deviceStore = useDeviceStore()
  return _deviceStore
}

function tstore() {
  if (!_telemetryStore) _telemetryStore = useTelemetryStore()
  return _telemetryStore
}

export function useDeviceService() {
  const ts = tstore()
  const ds = dstore()

  const droneList = computed(() =>
    ts.droneIds.map((id) => {
      const t = ts.latestOf(id)
      return {
        id,
        name: id,
        model: 'Quadcopter V3',
        gateway: 'ORIN-001',
        battery: t?.battery_level ?? 0,
        status: (t ? 'FLYING' : 'OFFLINE') as 'FLYING' | 'LANDING' | 'IDLE' | 'CHARGING' | 'OFFLINE',
        lat: t?.latitude ?? 0,
        lng: t?.longitude ?? 0,
        updatedAt: t?.recorded_at ?? '-',
      }
    })
  )

  return reactive({
    drones: droneList,
    gateways: ds.gateways,
    fetchGateways: () => ds.fetchGateways(),
    historyOf: (id: string) => ts.historyOf(id),
    isConnected: ts.connected,
  })
}
