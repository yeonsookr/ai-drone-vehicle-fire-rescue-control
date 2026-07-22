import { useDeviceStore } from '@/stores/device'
import { useTelemetryStore } from '@/stores/telemetry'

export function useDeviceService() {
  const ts = useTelemetryStore()
  const ds = useDeviceStore()

  return {
    get drones() {
      return ts.droneIds.map((id) => {
        const t = ts.latestOf(id)
        return {
          id, name: id, model: 'Quadcopter V3', gateway: 'ORIN-001',
          battery: t?.battery_level ?? 0,
          status: (t ? 'FLYING' : 'OFFLINE') as 'FLYING' | 'LANDING' | 'IDLE' | 'CHARGING' | 'OFFLINE',
          lat: t?.latitude ?? 0, lng: t?.longitude ?? 0,
          updatedAt: t?.recorded_at ?? '-',
        }
      })
    },
    get vehicles() {
      return ts.vehicleIds.map((id) => {
        const t = ts.vehicleLatestOf(id)
        return {
          id, name: id, model: 'OrinCar', gateway: 'ORIN-001',
          battery: t?.battery_level ?? 0,
          status: (t ? 'MOVING' : 'OFFLINE') as 'idle' | 'moving' | 'stopped' | 'error' | 'offline',
          lat: t?.latitude ?? 0, lng: t?.longitude ?? 0,
          updatedAt: t?.recorded_at ?? '-',
        }
      })
    },
    get gateways() { return ds.gateways },
    get connected() { return ts.connected },
    fetchGateways: () => ds.fetchGateways(),
    historyOf: (id: string) => ts.historyOf(id),
    vehicleHistoryOf: (id: string) => ts.vehicleHistoryOf(id),
  }
}
