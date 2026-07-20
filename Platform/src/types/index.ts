export type DroneStatus = 'docked' | 'flying' | 'returning' | 'landing' | 'error' | 'offline'
export type GatewayStatus = 'online' | 'offline' | 'error'
export type DetectionType = 'forest_fire' | 'smoke' | 'distressed_person'
export type OperatorJudgment = 'unconfirmed' | 'approved' | 'false_alarm' | 'pending'
export type MissionType = 'patrol' | 'dispatch' | 'fire_response'
export type MissionStatus = 'CREATED' | 'ASSIGNED' | 'DISPATCHED' | 'IN_PROGRESS' | 'COMPLETED' | 'PAUSED' | 'RETURNING' | 'FAILED' | 'CANCELLED'

export interface Drone {
  id: string
  name: string
  type: 'real' | 'mock'
  status: DroneStatus
  battery_level: number
  current_lat: number
  current_lng: number
  current_alt: number
  created_at: string
  updated_at: string
}

export interface Gateway {
  id: string
  name: string
  status: GatewayStatus
  ip_address: string
  last_heartbeat_at: string
  created_at: string
  updated_at: string
}

export interface DroneTelemetry {
  drone_id: string
  latitude: number
  longitude: number
  altitude: number
  speed: number
  battery_level: number
  pitch: number
  roll: number
  yaw: number
  signal_strength: number
  recorded_at: string
}

export interface AiDetection {
  id: string
  mission_id: string | null
  drone_id: string | null
  vehicle_id: string | null
  detection_type: DetectionType
  confidence: number
  bounding_box: { x: number; y: number; w: number; h: number }
  latitude: number
  longitude: number
  snapshot_url: string
  model_version: string
  source: 'edge_ai_orin' | 'server_gpu'
  operator_judgment: OperatorJudgment
  operator_id: number | null
  judged_at: string | null
  judgment_reason: string | null
  detected_at: string
  created_at: string
}

export interface DashboardSummary {
  active_drones: number
  online_gateways: number
  streaming_count: number
  active_alerts: number
}
