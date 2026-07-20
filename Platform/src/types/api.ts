import type {
  Drone, DroneTelemetry,
  Vehicle, VehicleTelemetry,
  Gateway, DevicePairing,
  Mission, MissionWaypoint, MissionLog, MissionType,
  Command, CommandType, CommandTargetType,
  AiDetection, DetectionType, OperatorJudgment,
  FirePrediction, VideoStream,
  DroneStatus, VehicleStatus, MissionStatus, Timestamp,
} from './models'

// ── 공통 응답 래퍼 ──
export interface ApiResponse<T> {
  data: T
  message?: string
}

export interface PageResponse<T> {
  content: T[]
  total_elements: number
  total_pages: number
  page: number
  size: number
}

// ── 드론 API ──
export interface DroneListParams {
  status?: DroneStatus
  gateway_id?: string
}

export interface DroneTelemetryParams {
  range?: 'realtime' | '1h' | '6h' | '24h'
  from?: Timestamp
  to?: Timestamp
}

export interface DroneApi {
  list(params?: DroneListParams): Promise<ApiResponse<Drone[]>>
  get(id: string): Promise<ApiResponse<Drone>>
  telemetry(id: string, params?: DroneTelemetryParams): Promise<ApiResponse<DroneTelemetry[]>>
}

// ── 게이트웨이 API ──
export interface GatewayApi {
  list(): Promise<ApiResponse<Gateway[]>>
  get(id: string): Promise<ApiResponse<Gateway>>
  heartbeat(id: string): Promise<ApiResponse<void>>
}

// ── 차량 API ──
export interface VehicleApi {
  list(params?: { status?: VehicleStatus }): Promise<ApiResponse<Vehicle[]>>
  get(id: string): Promise<ApiResponse<Vehicle>>
  telemetry(id: string, params?: { range?: string }): Promise<ApiResponse<VehicleTelemetry[]>>
  pairings(id: string): Promise<ApiResponse<DevicePairing[]>>
}

// ── 임무 API ──
export interface MissionCreateRequest {
  type: MissionType
  vehicle_id: string
  drone_id: string
  waypoints?: Omit<MissionWaypoint, 'id' | 'mission_id' | 'created_at'>[]
}

export interface MissionApi {
  list(params?: { status?: MissionStatus; type?: MissionType }): Promise<ApiResponse<Mission[]>>
  get(id: string): Promise<ApiResponse<Mission>>
  create(req: MissionCreateRequest): Promise<ApiResponse<Mission>>
  updateStatus(id: string, status: MissionStatus): Promise<ApiResponse<Mission>>
  waypoints(id: string): Promise<ApiResponse<MissionWaypoint[]>>
  logs(id: string): Promise<ApiResponse<MissionLog[]>>
}

// ── 명령 API ──
export interface CommandRequest {
  target_type: CommandTargetType
  target_id: string
  type: CommandType
  parameters?: Record<string, unknown>
  expires_sec?: number
}

export interface CommandApi {
  send(req: CommandRequest): Promise<ApiResponse<Command>>
  list(mission_id?: string): Promise<ApiResponse<Command[]>>
  get(id: string): Promise<ApiResponse<Command>>
}

// ── AI 탐지 API ──
export interface DetectionListParams {
  judgment?: OperatorJudgment
  type?: DetectionType
  limit?: number
  offset?: number
}

export interface DetectionJudgeRequest {
  judgment: OperatorJudgment
  reason?: string
}

export interface DetectionApi {
  list(params?: DetectionListParams): Promise<ApiResponse<AiDetection[]>>
  get(id: string): Promise<ApiResponse<AiDetection>>
  judge(id: string, req: DetectionJudgeRequest): Promise<ApiResponse<AiDetection>>
  predictions(event_id: string): Promise<ApiResponse<FirePrediction[]>>
}

// ── 영상 스트림 API ──
export interface StreamApi {
  list(mission_id?: string): Promise<ApiResponse<VideoStream[]>>
}

// ── 대시보드 API ──
export interface DashboardSummary {
  active_drones: number
  online_gateways: number
  active_vehicles: number
  streaming_count: number
  active_alerts: number
  active_missions: number
}

export interface DashboardApi {
  summary(): Promise<ApiResponse<DashboardSummary>>
}

// ── SSE 이벤트 ──
export type SseEventType = 'telemetry' | 'detection' | 'alert' | 'status' | 'command'

export interface SseEvent<T = unknown> {
  event: SseEventType
  data: T
}

export interface TelemetryEvent {
  drone_id: string
  latitude: number
  longitude: number
  altitude: number
  speed: number
  battery_level: number
  heading: number
  recorded_at: Timestamp
}

export interface DetectionEvent {
  id: string
  detection_type: DetectionType
  confidence: number
  latitude: number
  longitude: number
  snapshot_url: string
  detected_at: Timestamp
}

export interface AlertEvent {
  type: 'emergency' | 'warning' | 'info'
  drone_id?: string
  message: string
  timestamp: Timestamp
}

export interface StatusEvent {
  drone_id: string
  status: DroneStatus
  timestamp: Timestamp
}
