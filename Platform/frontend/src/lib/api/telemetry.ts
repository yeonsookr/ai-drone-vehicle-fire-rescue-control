import type { DroneTelemetry, VehicleTelemetry } from '@/types'

type TelemetryCallback = (entry: DroneTelemetry) => void

// Mock implementation. Rewrite to use EventSource when backend is ready.

let intervalId: ReturnType<typeof setInterval> | null = null
let counter = 0

const DRONE_IDS = ['DRONE-001', 'DRONE-002', 'DRONE-003', 'DRONE-004']
const BASE_POSITIONS: Record<string, { lat: number; lng: number; alt: number }> = {
  'DRONE-001': { lat: 37.5665, lng: 126.9780, alt: 120 },
  'DRONE-002': { lat: 37.5512, lng: 126.9885, alt: 95 },
  'DRONE-003': { lat: 37.5789, lng: 126.9700, alt: 150 },
  'DRONE-004': { lat: 37.5600, lng: 126.9950, alt: 80 },
}

function stepPos(base: number, tick: number, offset: number): number {
  const angle = (tick * 0.05 + offset) * (Math.PI / 180)
  return base + Math.sin(angle) * 0.02
}

function generate(): DroneTelemetry {
  counter++
  const idx = counter % DRONE_IDS.length
  const id = DRONE_IDS[idx]
  const base = BASE_POSITIONS[id]

  return {
    drone_id: id,
    latitude: stepPos(base.lat, counter, idx * 90),
    longitude: stepPos(base.lng, counter, idx * 90 + 30),
    altitude: base.alt + Math.sin(counter * 0.1 + idx) * 20,
    speed: 10 + Math.sin(counter * 0.05 + idx) * 5,
    battery_level: Math.max(0, 85 - counter * 0.02),
    pitch: 0,
    roll: 0,
    yaw: 0,
    signal_strength: -60 + Math.random() * 20,
    raw_data: null,
    recorded_at: new Date().toISOString(),
  }
}

export function subscribeTelemetry(callback: TelemetryCallback): () => void {
  // Push one entry per second, rotating through drones
  intervalId = setInterval(() => {
    callback(generate())
  }, 250)

  return () => {
    if (intervalId !== null) {
      clearInterval(intervalId)
      intervalId = null
    }
  }
}

// ── Vehicle telemetry ──
let vehicleIntervalId: ReturnType<typeof setInterval> | null = null
let vehicleCounter = 0

const VEHICLE_IDS = ['VEH-001', 'VEH-002', 'VEH-003']
const VEHICLE_POSITIONS: Record<string, { lat: number; lng: number; alt: number }> = {
  'VEH-001': { lat: 37.5680, lng: 126.9770, alt: 20 },
  'VEH-002': { lat: 37.5540, lng: 126.9910, alt: 18 },
  'VEH-003': { lat: 37.5750, lng: 126.9720, alt: 22 },
}

function generateVehicle(): VehicleTelemetry {
  vehicleCounter++
  const idx = vehicleCounter % VEHICLE_IDS.length
  const id = VEHICLE_IDS[idx]
  const base = VEHICLE_POSITIONS[id]

  return {
    vehicle_id: id,
    latitude: stepPos(base.lat, vehicleCounter, idx * 120),
    longitude: stepPos(base.lng, vehicleCounter, idx * 120 + 45),
    altitude: base.alt + Math.sin(vehicleCounter * 0.08 + idx) * 5,
    speed: 3 + Math.sin(vehicleCounter * 0.04 + idx) * 2,
    battery_level: Math.max(0, 85 - vehicleCounter * 0.01),
    pitch: 0,
    roll: 0,
    yaw: 0,
    signal_strength: -60 + Math.random() * 20,
    raw_data: null,
    recorded_at: new Date().toISOString(),
  }
}

export function subscribeVehicleTelemetry(callback: (entry: VehicleTelemetry) => void): () => void {
  vehicleIntervalId = setInterval(() => {
    callback(generateVehicle())
  }, 350)

  return () => {
    if (vehicleIntervalId !== null) {
      clearInterval(vehicleIntervalId)
      vehicleIntervalId = null
    }
  }
}
