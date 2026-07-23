# Jetson Orin Continuous Edge AI Server

드론 내장 CPU에서 차량 Jetson Orin으로 전달되는 영상 프레임을 상시 추론하고, 탐지 정보를 중앙 Spring 백엔드로 먼저 전송하는 Edge AI 서버입니다. 통신은 프로젝트 문서에 맞춰 **MQTT 제어·메타데이터**와 **HTTP 고용량 이미지**로 분리합니다.

## 통신 흐름

```text
드론 영상 수신 어댑터
   │ HTTP/로컬 호출: 이미지 프레임
   ▼
Jetson bounded frame queue
   │ 상시 AI 추론
   ├─ MQTT ──> 백엔드: AI 이벤트 메타데이터
   └─ HTTP ──> 백엔드: 탐지 스냅샷 파일

백엔드
   ├─ MQTT ──> Jetson: capture / burst_capture / reanalyze
   ├─ MQTT <── Jetson: ACK / RUNNING / SUCCEEDED / FAILED / EXPIRED
   └─ MQTT ──> Jetson: 관제자 승인·오탐·보류 피드백
```

백엔드가 사진을 Jetson에 첨부하여 추론시키는 구조가 아닙니다. 드론 영상 수신 프로세스가 Jetson 내부 HTTP 입력 경계로 프레임을 계속 넣고, 중앙 백엔드는 MQTT로 추가 작업만 지시합니다.

이 서버는 GPIO·모터·비행 제어기를 직접 조작하지 않습니다. `capture`와 `burst_capture`는 명령 이후 Jetson에 들어오는 드론 프레임을 확보합니다. 실제 드론에 촬영 신호를 보내는 기능은 Embedded 파트의 승인된 명령 어댑터에 연결해야 합니다.

## MQTT 계약

기본 QoS는 `1`입니다.

| 방향 | Topic | Payload |
|---|---|---|
| Backend → Jetson | `vehicle/{vehicleId}/command` | 현재 Spring `CommandService` 호환 명령 |
| Backend → Jetson | `vehicle/{vehicleId}/ai/command` | 추가 촬영·재분석 명령 |
| Jetson → Backend | `vehicle/{vehicleId}/ai/command/{commandId}/status` | 명령 ACK와 수행 상태 |
| Jetson → Backend | `vehicle/{vehicleId}/ai/events` | 탐지 종류·신뢰도·경계 상자·위치·모델 버전 |
| Backend → Jetson | `vehicle/{vehicleId}/ai/feedback` | 관제자 승인·오탐·보류 판정 |
| Jetson → Backend | `vehicle/{vehicleId}/ai/feedback/{frameId}/status` | 피드백 수신 결과 |
| Jetson → Backend | `vehicle/{vehicleId}/ai/status` | retained 상태와 heartbeat |

### AI 이벤트 예시

```json
{
  "schemaVersion": "1.0",
  "eventId": "edge-D-01-20260723-093000-001",
  "frameId": "D-01-20260723-093000-001",
  "missionId": "M-001",
  "vehicleId": "V-01",
  "droneId": "D-01",
  "detectedAt": "2026-07-23T09:30:00.000",
  "location": {"latitude": 37.52412, "longitude": 127.02534, "altitude": 42.5},
  "modelVersion": "wildfire-orin-v1.0.0",
  "detections": [
    {
      "detectionType": "smoke",
      "confidence": 0.87,
      "boundingBox": {"x": 10, "y": 20, "w": 30, "h": 40},
      "operatorAction": "confirm_required"
    }
  ],
  "snapshotTransport": "http",
  "snapshotUploadState": "queued"
}
```

### 추가 촬영 명령

```json
{
  "commandId": "cmd-001",
  "type": "burst_capture",
  "targetId": "V-01",
  "issuedAt": "2026-07-23T09:31:00Z",
  "expiresAt": "2026-07-23T09:31:30Z",
  "parameters": {"count": 3}
}
```

지원 명령:

- `capture`: 명령 이후 들어오는 프레임 1장 확보
- `burst_capture`: 명령 이후 들어오는 프레임 1~10장 확보
- `reanalyze`: `parameters.frameId`의 버퍼 프레임 재분석. 생략 시 최신 프레임 사용

명령은 `commandId` 중복, 대상 차량, 만료 시각을 검증합니다. 상태는 `ACK → RUNNING → SUCCEEDED | FAILED | EXPIRED` 순서로 같은 command status topic에 발행합니다.

문서에는 세부 MQTT topic이 아직 확정되지 않았습니다. 현재 Spring 백엔드는 `vehicle/{id}/command`와 snake_case payload를 사용하므로 이 서버는 해당 계약과 위 AI 전용 topic을 함께 구독합니다. Spring payload에 `expires_at`이 없으면 현재 백엔드 DB 정책과 같은 30초 TTL을 적용합니다.

### 관제자 피드백

```json
{
  "requestId": "D-01-20260723-093000-001",
  "eventId": "det-backend-id",
  "judgment": "approved",
  "reason": "원본 영상에서 연기 확인",
  "judgedAt": "2026-07-23T09:32:00Z"
}
```

`judgment`는 `approved`, `false_alarm`, `pending` 중 하나입니다. 현재는 bounded 메모리 캐시에 저장하며 자동 재학습이나 장비 제어로 연결하지 않습니다.

## HTTP 계약

HTTP는 이미지와 영상처럼 크기가 큰 데이터에 사용합니다.

### Jetson 내부 입력·진단 API

| 메서드 | 경로 | 용도 |
|---|---|---|
| `GET` | `/health` | 프로세스 생존 확인 |
| `GET` | `/api/v1/ai/status` | 모델·프레임·MQTT 상태 진단 |
| `POST` | `/api/v1/ai/frames` | Jetson 내부 드론 수신기가 프레임 입력 |
| `GET` | `/api/v1/ai/results/{frameId}` | 로컬 추론 결과 진단 |
| `GET` | `/api/v1/ai/frames/{frameId}` | bounded 버퍼의 원본 프레임 조회 |
| `GET` | `/api/v1/ai/commands/{commandId}` | MQTT 명령의 로컬 상태 진단 |
| `GET` | `/api/v1/ai/feedback/{frameId}` | MQTT 피드백의 로컬 상태 진단 |
| `POST` | `/api/v1/ai/video-stream` | 중앙 백엔드에 영상 URL 등록 |

HTTP로 명령이나 관제 피드백을 받지 않습니다. `POST /api/v1/ai/commands`와 `POST /api/v1/ai/feedback`은 존재하지 않습니다.

`/api/v1/*` 요청은 `Authorization: Bearer <EDGE_AI_API_TOKEN>` 또는 `X-Edge-Token` 인증이 필요합니다.

### 드론 프레임 입력

`POST /api/v1/ai/frames`, `multipart/form-data`

- `file`: `image/jpeg` 또는 `image/png`
- `metadata`: JSON 문자열

```json
{
  "frameId": "D-01-20260723-093000-001",
  "missionId": "M-001",
  "sourceDroneId": "D-01",
  "capturedAt": "2026-07-23T09:30:00",
  "latitude": 37.52412,
  "longitude": 127.02534,
  "altitude": 42.5
}
```

응답은 추론 결과가 아니라 큐 접수 결과인 `202 Accepted`입니다. 입력 FPS가 추론 속도보다 빠르면 오래된 대기 프레임을 제거하고 최신 프레임을 우선합니다. 운영 시 드론 수신 어댑터에서 AI 입력 FPS에 맞게 샘플링해야 합니다.

### 탐지 스냅샷 업로드

탐지 발생 시 MQTT 이벤트를 먼저 발행하고, 이미지 파일은 현재 Spring 계약인 `POST /api/detections/snapshot`으로 업로드합니다. 메타데이터는 `missionId`, `deviceId`, `deviceType`, `detectionType`, `confidence`, `boundingBox`, 위치, `detectedAt`, `modelVersion`, `source`를 포함합니다.

처음 탐지된 종류는 기본 10초 안에 최대 3개 근거 프레임을 선제 전송합니다. 이후 같은 종류는 기본 30초 cooldown을 적용합니다.

AI 탐지가 없는 추가 사진은 현재 백엔드의 탐지 전용 API로 영구 저장할 수 없으므로 명령 결과의 `frameUrl`로 조회합니다. 모든 추가 사진을 저장하려면 Backend에 일반 증거 이미지 업로드 API가 추가되어야 합니다.

## 현재 Spring 백엔드와의 연결 차이

현재 `Server/IoTServer`는 텔레메트리 MQTT 구독과 `vehicle/{id}/command` 발행까지만 구현되어 있습니다. 실제 통합을 위해 Backend에 다음 작업이 추가되어야 합니다.

- `vehicle/{id}/ai/events`, `vehicle/{id}/ai/status`, command status, feedback status 구독
- 최종 MQTT topic 계약 확정 후 `vehicle/{id}/command`와 AI 전용 topic 중 하나로 통일
- 명령 payload에 `expiresAt` 포함 권장(누락 시 Jetson이 기본 30초 적용)
- 관제 판정을 `vehicle/{id}/ai/feedback`으로 발행
- MQTT event와 HTTP snapshot을 `frameId` 또는 `eventId`로 연결

## 실행

MQTT 런타임은 `paho-mqtt`를 사용합니다. 실제 Jetson 환경에서만 설치합니다.

```bash
cd /path/to/S15P11A302/AI
python3 -m pip install -r edge_ai_server/requirements.txt
cp edge_ai_server/.env.example .env
# .env의 토큰, MQTT broker, 백엔드 주소, 모델 경로 수정
python3 -m edge_ai_server
```

실제 모델 엔진은 기존 Jetson 환경의 `ultralytics`와 PyTorch를 지연 로딩합니다. 실제 토큰과 MQTT 비밀번호가 들어 있는 `.env`는 커밋하지 않습니다.

## 테스트

실제 broker·카메라·GPU·GPIO 없이 fake MQTT transport로 계약을 검증합니다.

```powershell
cd C:\Users\SSAFY\Desktop\MVP전처리학습\S15P11A302\AI
python -m compileall -q edge_ai_server
python -m unittest discover -s edge_ai_server\tests -v
```

## 운영 안전 기준

- MQTT 명령은 대상·중복·만료를 확인하고 QoS 1로 처리합니다.
- MQTT 연결 실패 중 발행 메시지는 bounded 메모리 큐에 보관하고 heartbeat 시 재전송을 시도합니다.
- GPU 추론은 하나씩 실행하여 Jetson 메모리 급증을 방지합니다.
- 프레임 큐·버퍼·결과 캐시·전송 큐는 모두 크기가 제한됩니다.
- AI 결과나 MQTT 명령을 실제 차량·드론 제어로 직접 연결하지 않습니다.
- Spring 백엔드는 아직 `X-Idempotency-Key`를 저장하지 않으므로 HTTP 응답 유실 후 재시도 시 중복 탐지 이벤트 가능성이 있습니다.
