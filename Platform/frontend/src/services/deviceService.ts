import { useDeviceStore } from '@/stores/device'
import { useTelemetryStore } from '@/stores/telemetry'
import type { DroneTelemetry, VehicleTelemetry } from '@/types'

export interface EquipmentCard {
  id: string
  label: string
  type: 'drone' | 'vehicle'
  battery: number
  altitude: number
  speed: number
  signal: number
  stale: boolean
}

function isStale(recordedAt: string): boolean {
  return Date.now() - new Date(recordedAt).getTime() > 4000
}

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
    get equipmentCards(): EquipmentCard[] {
      const cards: EquipmentCard[] = []
      for (const id of ts.droneIds) {
        const t = ts.latestOf(id)
        if (!t) continue
        cards.push({
          id, label: id, type: 'drone',
          battery: t.battery_level, altitude: t.altitude, speed: t.speed, signal: t.signal_strength,
          stale: isStale(t.recorded_at),
        })
      }
      for (const id of ts.vehicleIds) {
        const t = ts.vehicleLatestOf(id)
        if (!t) continue
        cards.push({
          id, label: id, type: 'vehicle',
          battery: t.battery_level, altitude: t.altitude, speed: t.speed, signal: t.signal_strength,
          stale: isStale(t.recorded_at),
        })
      }
      return cards
    },
    get disconnectedDevices(): EquipmentCard[] {
      return this.equipmentCards.filter(c => c.stale || c.signal < -85)
    },
    get gateways() { return ds.gateways },
    get connected() { return ts.connected },
    fetchGateways: () => ds.fetchGateways(),
    historyOf: (id: string) => ts.historyOf(id),
    vehicleHistoryOf: (id: string) => ts.vehicleHistoryOf(id),
    deviceHistoryOf(id: string): (DroneTelemetry | VehicleTelemetry)[] {
      const drone = ts.historyOf(id)
      if (drone.length > 0) return drone
      return ts.vehicleHistoryOf(id)
    },
  }
}
