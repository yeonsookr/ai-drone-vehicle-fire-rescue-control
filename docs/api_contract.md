# 엣지(Jetson Orin) ↔ 관제 서버 HTTP API 규격서 (v1.0)

본 문서는 **차량용 Jetson Orin(Edge) 및 AI 모델**과 **통합 관제 서버** 간의 고용량 영상/사진 통신용 HTTP API 명세서입니다.

---

## 1. 실시간 영상 스트리밍 세션 등록 API

젯슨 오린의 Flask 카메라 서버가 구동될 때, 현재 생성된 스트리밍 URL을 관제 서버에 동적으로 보고하는 엔드포인트입니다.

- **메서드 및 경로**: `POST /api/video-streams`
- **요청 Content-Type**: `application/json`

### 1.1 요청 페이로드 (Request Body JSON)

| 필드명 | 타입 | 필수 여부 | 설명 | 예시 |
|---|---|---|---|---|
| `deviceId` | String | **필수** | 스트리밍을 송신하는 물리 장비 ID | `"D-01"` / `"V-01"` |
| `deviceType` | String | **필수** | 장비의 종류 (`drone` 또는 `vehicle`) | `"drone"` |
| `streamUrl` | String | **필수** | 젯슨 내부에서 기동된 Flask 스트리밍 주소 | `"http://192.168.0.15:5000/live"` |
| `status` | String | **필수** | 스트리밍 상태 (`streaming`, `inactive`, `error`) | `"streaming"` |
| `missionId` | String | *선택* | 현재 수행 중인 임무 ID | `"M-001"` |

```json
{
  "deviceId": "D-01",
  "deviceType": "drone",
  "streamUrl": "http://192.168.0.15:5000/live",
  "status": "streaming",
  "missionId": "M-001"
}
```

### 1.2 응답 페이로드 (Response Body JSON)

#### 성공 (`200 OK` 또는 `201 Created`)
```json
{
  "status": "success",
  "message": "Stream URL registered successfully",
  "streamId": 12
}
```

#### 실패 (`400 Bad Request` - 필수 필드 누락 등)
```json
{
  "status": "error",
  "message": "Required field 'streamUrl' is missing"
}
```

---

## 2. AI 스냅샷 및 이상 탐지 이벤트 수신 API

차량(OrinCar) 내 젯슨 오린의 AI(YOLO) 모델이 산불/연기/조난자를 탐지했을 때, 감지 스냅샷 이미지 파일과 세부 메타데이터를 함께 서버로 일괄 업로드하는 엔드포인트입니다.

- **메서드 및 경로**: `POST /api/detections/snapshot`
- **요청 Content-Type**: `multipart/form-data`

### 2.1 요청 파트 명세 (Multipart Parts)

요청은 반드시 아래의 두 가지 파트를 포함해야 합니다.

1. **`file` Part**
   - **타입**: File (`image/jpeg` 또는 `image/png` 파일 스트림)
   - **설명**: AI 감지 순간의 캡처 정지 화면 스냅샷 파일.
2. **`metadata` Part**
   - **타입**: String (JSON 형식)
   - **Content-Type**: `application/json` 지정 필요.
   - **설명**: 감지 지점의 GPS 위치, 탐지 타입, AI 신뢰도 등의 정보.

#### `metadata` JSON 구조 상세

| 필드명 | 타입 | 필수 여부 | 설명 | 예시 |
|---|---|---|---|---|
| `missionId` | String | *선택* | 감지 시점에 수행 중이던 임무 ID | `"M-001"` |
| `deviceId` | String | **필수** | AI 추론을 수행한 장치 ID (젯슨 탑재 차량 ID) | `"V-01"` |
| `deviceType` | String | **필수** | 추론 장치 유형 (`vehicle`) | `"vehicle"` |
| `detectionType` | String | **필수** | 탐지 분류 (`forest_fire`: 산불, `smoke`: 연기, `distressed_person`: 조난자) | `"forest_fire"` |
| `confidence` | Double | **필수** | AI 모델의 검출 신뢰도 확률 (0.0 ~ 1.0) | `0.95` |
| `latitude` | Double | **필수** | 탐지 발생 위치 위도 | `37.52412` |
| `longitude` | Double | **필수** | 탐지 발생 위치 경도 | `127.02534` |
| `detectedAt` | String | **필수** | 젯슨에서 객체 감지가 처음 발생한 시각 (ISO-8601) | `"2026-07-22T10:10:00"` |

```json
{
  "missionId": "M-001",
  "deviceId": "V-01",
  "deviceType": "vehicle",
  "detectionType": "forest_fire",
  "confidence": 0.95,
  "latitude": 37.52412,
  "longitude": 127.02534,
  "detectedAt": "2026-07-22T10:10:00"
}
```

### 2.2 응답 페이로드 (Response Body JSON)

#### 성공 (`201 Created`)
업로드 완료 시 저장된 이미지 파일을 브라우저에서 볼 수 있는 정적 웹 주소(`imageUrl`)를 반환합니다.
```json
{
  "status": "success",
  "message": "AI detection snapshot uploaded successfully",
  "detectionId": "det-6cb39c87-8d71-47dc-992e-639a88699b75",
  "imageUrl": "/uploads/detections/det-6cb39c87-8d71-47dc-992e-639a88699b75.jpg"
}
```

#### 실패 (`400 Bad Request` - 잘못된 DTO 포맷 또는 파일 누락)
```json
{
  "status": "error",
  "message": "Required multipart part 'file' is missing"
}
```
