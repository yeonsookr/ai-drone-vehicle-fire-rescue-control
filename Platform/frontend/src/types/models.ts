// ── 공통 ──
export type DeviceType = 'real' | 'mock'
export type Timestamp = string // ISO8601

// ── 사용자 ──
export type UserRole = 'admin' | 'operator' | 'viewer'

export interface User {
  id: number
  username: string
  role: UserRole
  created_at: Timestamp
  updated_at: Timestamp
}

// ── 게이트웨이 ──
export type GatewayStatus = 'online' | 'offline' | 'error'

export interface Gateway {
  id: string
  name: string
  status: GatewayStatus
  ip_address: string | null
  last_heartbeat_at: Timestamp | null
  created_at: Timestamp
  updated_at: Timestamp
}

// ── 차량 (OrinCar) ──
export type VehicleStatus = 'idle' | 'moving' | 'stopped' | 'error' | 'offline'

export interface Vehicle {
  id: string
  gateway_id: string | null
  name: string
  type: DeviceType
  status: VehicleStatus
  battery_level: number
  current_lat: number
  current_lng: number
  current_alt: number
  created_at: Timestamp
  updated_at: Timestamp
}

// ── 드론 ──
export type DroneStatus = 'docked' | 'flying' | 'returning' | 'landing' | 'error' | 'offline'

export interface Drone {
  id: string
  name: string
  type: DeviceType
  status: DroneStatus
  battery_level: number
  current_lat: number
  current_lng: number
  current_alt: number
  created_at: Timestamp
  updated_at: Timestamp
}

// ── 장비 페어링 ──
export type LoadStatus = 'docked' | 'deployed'

export interface DevicePairing {
  id: number
  vehicle_id: string
  drone_id: string
  load_status: LoadStatus
  is_active: boolean
  paired_at: Timestamp
  unpaired_at: Timestamp | null
}

// ── 텔레메트리 ──
export interface VehicleTelemetry {
  vehicle_id: string
  latitude: number
  longitude: number
  altitude: number
  speed: number
  battery_level: number
  pitch: number
  roll: number
  yaw: number
  signal_strength: number
  raw_data: Record<string, unknown> | null
  recorded_at: Timestamp
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
  raw_data: Record<string, unknown> | null
  recorded_at: Timestamp
}

// ── 임무 ──
export type MissionType = 'patrol' | 'dispatch' | 'fire_response'
export type MissionStatus =
  | 'CREATED' | 'ASSIGNED' | 'DISPATCHED' | 'IN_PROGRESS'
  | 'COMPLETED' | 'PAUSED' | 'RETURNING' | 'FAILED' | 'CANCELLED'

export interface Mission {
  id: string
  type: MissionType
  status: MissionStatus
  vehicle_id: string
  drone_id: string
  assigned_at: Timestamp | null
  started_at: Timestamp | null
  completed_at: Timestamp | null
  created_by: number
  created_at: Timestamp
  updated_at: Timestamp
  failure_reason: string | null
}

export interface MissionWaypoint {
  id: number
  mission_id: string
  sequence_number: number
  latitude: number
  longitude: number
  altitude: number
  speed: number
  action: 'none' | 'take_photo' | 'hover' | 'land'
  created_at: Timestamp
}

export interface MissionLog {
  id: number
  mission_id: string
  status_from: string
  status_to: string
  reason: string | null
  changed_by: 'operator' | 'edge_ai' | 'safety_policy'
  user_id: number | null
  created_at: Timestamp
}

// ── 명령 ──
export type CommandTargetType = 'vehicle' | 'drone'
export type CommandType = 'move' | 'return' | 'stop' | 'pause' | 'resume' | 'manual_control'
export type CommandStatus = 'ACK' | 'RUNNING' | 'SUCCEEDED' | 'FAILED' | 'EXPIRED'
export type CommandIssuer = 'operator' | 'edge_ai' | 'safety_policy'

export interface Command {
  id: string
  parent_command_id: string | null
  mission_id: string | null
  target_type: CommandTargetType
  target_id: string
  type: CommandType
  status: CommandStatus
  issuer: CommandIssuer
  operator_id: number | null
  parameters: Record<string, unknown> | null
  error_reason: string | null
  issued_at: Timestamp
  expires_at: Timestamp
  completed_at: Timestamp | null
}

// ── AI 탐지 ──
export type DetectionType = 'forest_fire' | 'smoke' | 'distressed_person'
export type DetectionSource = 'edge_ai_orin' | 'server_gpu'
export type OperatorJudgment = 'unconfirmed' | 'approved' | 'false_alarm' | 'pending'

export interface BoundingBox {
  x: number
  y: number
  w: number
  h: number
}

export interface AiDetection {
  id: string
  mission_id: string | null
  drone_id: string | null
  vehicle_id: string | null
  detection_type: DetectionType
  confidence: number
  bounding_box: BoundingBox
  latitude: number
  longitude: number
  altitude: number
  snapshot_url: string
  model_version: string
  source: DetectionSource
  operator_judgment: OperatorJudgment
  operator_id: number | null
  judged_at: Timestamp | null
  judgment_reason: string | null
  detected_at: Timestamp
  created_at: Timestamp
}

// ── 산불 확산 예측 ──
export interface FirePrediction {
  id: number
  event_id: string
  model_version: string
  weather_wind_speed: number
  weather_wind_direction: number
  weather_humidity: number
  weather_temperature: number
  prediction_polygon: number[][][]
  created_at: Timestamp
}

// ── 영상 스트림 ──
export type StreamDeviceType = 'vehicle' | 'drone'
export type StreamStatus = 'streaming' | 'inactive' | 'error'

export interface VideoStream {
  id: number
  mission_id: string | null
  device_type: StreamDeviceType
  device_id: string
  stream_url: string
  status: StreamStatus
  started_at: Timestamp
  ended_at: Timestamp | null
}

// ── 감사 로그 ──
export interface AuditLog {
  id: number
  user_id: number | null
  action: string
  ip_address: string
  details: string | null
  created_at: Timestamp
}
