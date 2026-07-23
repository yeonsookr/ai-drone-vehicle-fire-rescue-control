# 관제 서버 ➔ 플랫폼 백엔드 데이터 전송 콜백 API 명세서 (v1.0)

본 문서는 통합 관제 서버(IoTServer, Port 8080)가 현장 장비로부터 수집한 실시간 위치 정보(텔레메트리) 및 AI 탐지 이벤트를 플랫폼 백엔드 서버(Port 8081)로 실시간 전달(Forwarding)할 때 수신해야 하는 REST 콜백 API 명세서입니다.

---

## 1. 드론 텔레메트리 1초 벌크 수신 콜백 API

드론들로부터 수신된 위치/배터리/자세 신호를 관제 서버가 1초 주기로 묶어서(Batch) 플랫폼 백엔드로 전송하는 엔드포인트입니다.

*   **메서드 및 경로**: `POST /api/callbacks/telemetry/drone`
*   **요청 Content-Type**: `application/json`

### 📋 요청 페이로드 (Request Body JSON Array)
```json
[
  {
    "drone_id": "D-01",
    "latitude": 37.52412,
    "longitude": 127.02534,
    "altitude": 15.5,
    "speed": 5.4,
    "battery_level": 88.5,
    "pitch": 0.1,
    "roll": -0.2,
    "yaw": 180.0,
    "signal_strength": 92.0,
    "recorded_at": "2026-07-23T13:00:00.000"
  }
]
```

### 🔍 필드 상세 명세
| 필드명 | 타입 | 설명 |
|---|---|---|
| `drone_id` | String | 드론 식별 고유 ID |
| `latitude` | Double | 현재 위도 좌표 (WGS84) |
| `longitude` | Double | 현재 경도 좌표 (WGS84) |
| `altitude` | Double | 비행 고도 (단위: m) |
| `speed` | Double | 이동 속도 (단위: m/s) |
| `battery_level` | Double | 배터리 잔량 (0.0 ~ 100.0 %) |
| `pitch` | Double | 피치 각도 (앞뒤 기울기) |
| `roll` | Double | 롤 각도 (좌우 기울기) |
| `yaw` | Double | 요 방위각 (0~360도) |
| `signal_strength` | Double | 통신 신호 세기 |
| `recorded_at` | String | 계측 발생 시각 (ISO-8601) |

---

## 2. 차량 텔레메트리 1초 벌크 수신 콜백 API

차량(게이트웨이)들로부터 수신된 위치/배터리 신호를 1초 주기로 묶어서 플랫폼 백엔드로 전송하는 엔드포인트입니다.

*   **메서드 및 경로**: `POST /api/callbacks/telemetry/vehicle`
*   **요청 Content-Type**: `application/json`

### 📋 요청 페이로드 (Request Body JSON Array)
```json
[
  {
    "vehicle_id": "V-01",
    "latitude": 37.52812,
    "longitude": 127.02934,
    "altitude": 20.0,
    "speed": 3.2,
    "battery_level": 92.0,
    "pitch": 0.0,
    "roll": 0.0,
    "yaw": 90.0,
    "signal_strength": 95.0,
    "recorded_at": "2026-07-23T13:00:00.000"
  }
]
```

---

## 3. AI 화재/조난자 감지 이벤트 수신 콜백 API

젯슨 오린 YOLO AI 모델이 산불/연기/조난자를 탐지하고 스냅샷 저장이 완료된 즉시, 플랫폼 백엔드로 긴급 경보 이벤트를 전송하는 엔드포인트입니다.

*   **메서드 및 경로**: `POST /api/callbacks/detections`
*   **요청 Content-Type**: `application/json`

### 📋 요청 페이로드 (Request Body JSON Object)
```json
{
  "detection_id": "det-6cb39c87-8d71-47dc-992e-639a88699b75",
  "mission_id": "M-001",
  "device_id": "D-01",
  "device_type": "drone",
  "detection_type": "forest_fire",
  "confidence": 0.95,
  "latitude": 37.52412,
  "longitude": 127.02534,
  "image_url": "/uploads/detections/det-6cb39c87-8d71-47dc-992e-639a88699b75.jpg",
  "detected_at": "2026-07-23T13:05:00.000"
}
```

### 🔍 필드 상세 명세
| 필드명 | 타입 | 설명 |
|---|---|---|
| `detection_id` | String | 감지 이벤트 고유 UUID |
| `mission_id` | String | 임무 ID (있을 경우) |
| `device_id` | String | 감지한 기기 ID |
| `device_type` | String | 기기 유형 (`drone` 또는 `vehicle`) |
| `detection_type` | String | 탐지 종류 (`forest_fire`: 산불, `smoke`: 연기, `distressed_person`: 조난자) |
| `confidence` | Double | AI 모델 신뢰도 (0.0 ~ 1.0) |
| `latitude` | Double | 감지 지점 위도 |
| `longitude` | Double | 감지 지점 경도 |
| `image_url` | String | 원본 고화질 스냅샷 이미지 웹 접근 주소 |
| `detected_at` | String | 탐지 발생 시각 (ISO-8601) |
