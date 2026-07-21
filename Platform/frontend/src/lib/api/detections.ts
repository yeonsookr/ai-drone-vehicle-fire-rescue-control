import type { AiDetection, DetectionJudgeRequest } from '@/types'

const MOCK_DETECTIONS: AiDetection[] = [
  { id: 'DET-001', mission_id: null, drone_id: 'DRONE-001', vehicle_id: null, detection_type: 'forest_fire', confidence: 0.92, bounding_box: { x: 100, y: 200, w: 50, h: 80 }, latitude: 37.5665, longitude: 126.9780, altitude: 0, snapshot_url: '', model_version: 'v1.0', source: 'edge_ai_orin', operator_judgment: 'unconfirmed', operator_id: null, judged_at: null, judgment_reason: null, detected_at: new Date().toISOString(), created_at: new Date().toISOString() },
  { id: 'DET-002', mission_id: null, drone_id: 'DRONE-002', vehicle_id: null, detection_type: 'smoke', confidence: 0.78, bounding_box: { x: 200, y: 150, w: 40, h: 60 }, latitude: 37.5512, longitude: 126.9885, altitude: 0, snapshot_url: '', model_version: 'v1.0', source: 'edge_ai_orin', operator_judgment: 'unconfirmed', operator_id: null, judged_at: null, judgment_reason: null, detected_at: new Date().toISOString(), created_at: new Date().toISOString() },
  { id: 'DET-003', mission_id: null, drone_id: 'DRONE-003', vehicle_id: null, detection_type: 'smoke', confidence: 0.65, bounding_box: { x: 80, y: 300, w: 30, h: 50 }, latitude: 37.5789, longitude: 126.9700, altitude: 0, snapshot_url: '', model_version: 'v1.0', source: 'edge_ai_orin', operator_judgment: 'approved', operator_id: null, judged_at: new Date().toISOString(), judgment_reason: 'Confirmed', detected_at: new Date().toISOString(), created_at: new Date().toISOString() },
  { id: 'DET-004', mission_id: null, drone_id: 'DRONE-001', vehicle_id: null, detection_type: 'forest_fire', confidence: 0.45, bounding_box: { x: 300, y: 180, w: 45, h: 70 }, latitude: 37.5600, longitude: 126.9950, altitude: 0, snapshot_url: '', model_version: 'v1.0', source: 'edge_ai_orin', operator_judgment: 'false_alarm', operator_id: null, judged_at: new Date().toISOString(), judgment_reason: 'No fire visible', detected_at: new Date().toISOString(), created_at: new Date().toISOString() },
]

export const detectionApi = {
  list: (params?: { judgment?: string; limit?: number }) => {
    let data = [...MOCK_DETECTIONS]
    if (params?.judgment) data = data.filter(d => d.operator_judgment === params.judgment)
    if (params?.limit) data = data.slice(0, params.limit)
    return Promise.resolve({ data, status: 200, statusText: 'OK', headers: {}, config: {} as any })
  },
  get: (id: string) => {
    const d = MOCK_DETECTIONS.find(d => d.id === id)
    return Promise.resolve({ data: d!, status: 200, statusText: 'OK', headers: {}, config: {} as any })
  },
  judge: (id: string, req: DetectionJudgeRequest) => {
    const d = MOCK_DETECTIONS.find(d => d.id === id)
    if (d) {
      d.operator_judgment = req.judgment
      d.judgment_reason = req.reason ?? null
      d.judged_at = new Date().toISOString()
    }
    return Promise.resolve({ data: d!, status: 200, statusText: 'OK', headers: {}, config: {} as any })
  },
}
