# MQTT 기기-서버 간 실시간 통신 규격 명세서 (MQTT Protocol Contract)

본 문서는 현장 장비(젯슨 오린 게이트웨이 및 드론)와 중앙 관제 서버(IoTServer) 간의 실시간 비동기 데이터 송수신(위치 텔레메트리, 수동 제어 명령 및 피드백)을 위한 MQTT 프로토콜 규격을 정의합니다.

---

## 1. 실시간 위치 및 상태 정보 상시 보고 (Telemetry)

드론 및 차량은 기동 중일 때 자신의 GPS 좌표와 기기 상태를 아래 규격에 맞춰 **1초 주기(1 Hz)**로 실시간 발행(Publish)해야 합니다.

*   **토픽 규격 (Topic)**:
    *   **드론**: `drone/{drone_id}/telemetry` (예: `drone/D-01/telemetry`)
    *   **차량**: `vehicle/{vehicle_id}/telemetry` (예: `vehicle/V-01/telemetry`)
*   **QoS 설정**: `0` (상시 고빈도 데이터이므로 지연 최소화를 위해 QoS 0 권장)

### 📋 JSON 메시지 규격 (Payload)
```json
{
  "latitude": 37.52412,
  "longitude": 127.02534,
  "altitude": 15.5,
  "speed": 5.4,
  "battery_level": 88.5,
  "pitch": 0.1,
  "roll": -0.2,
  "yaw": 180.0,
  "signal_strength": 92.0,
  "recorded_at": "2026-07-23T09:50:00.000Z",
  "raw_data": {
    "temperature": 28.5,
    "gps_satellite_count": 12
  }
}
```

### 🔍 필드 설명 (Field Details)
| 필드명 | 데이터 타입 | 필수 여부 | 설명 |
|---|---|:---:|---|
| `latitude` | Double | 필수 | 현재 위치의 위도 (WGS84 좌표계) |
| `longitude` | Double | 필수 | 현재 위치의 경도 (WGS84 좌표계) |
| `altitude` | Double | 필수 | 현재 위치의 고도 (드론: 이륙 기준 상대 고도, 차량: 해발 고도) |
| `speed` | Double | 필수 | 현재 이동 속도 (단위: m/s) |
| `battery_level` | Double | 필수 | 기기의 배터리 잔량 비율 (0.0 ~ 100.0 %) |
| `pitch` | Double | 필수 | 기기의 피치 각도 (X축 회전, 앞뒤 기울기) |
| `roll` | Double | 필수 | 기기의 롤 각도 (Y축 회전, 좌우 기울기) |
| `yaw` | Double | 필수 | 기기의 요 각도 (Z축 회전, 북 기준 0~360도 방위각) |
| `signal_strength` | Double | 선택 | 통신 신호 세기 (RSSI 값 등) |
| `recorded_at` | String | 필수 | 기기 단말에서 계측된 시각 (ISO 8601 UTC 표준 포맷) |
| `raw_data` | Object | 선택 | 추가 원시 센서 데이터 기록용 동적 맵 객체 |

---

## 2. 기기 원격 제어 명령 수신 (Device Control Command)

관제 서버가 기기를 제어(정지, 복귀, 조이스틱 수동 조종 등)하기 위해 발행하는 토픽으로, 젯슨 오린(기체)은 이 토픽을 **상시 구독(Subscribe)**하여 명령이 수신되는 즉시 하드웨어 구동을 통제해야 합니다.

*   **토픽 규격 (Topic)**:
    *   **드론 제어**: `drone/{drone_id}/command` (예: `drone/D-01/command`)
    *   **차량 제어**: `vehicle/{vehicle_id}/command` (예: `vehicle/V-01/command`)
*   **QoS 설정**: `1` (명령의 확실한 전달을 위해 QoS 1 적용)

### 📋 JSON 메시지 규격 (Payload)
```json
{
  "command_id": "cmd-6e8fdb08-023d-419b-87de-2dcaa7a08ece",
  "type": "manual_control",
  "parameters": {
    "joystick_x": 0.8,
    "joystick_y": -0.3
  },
  "issued_at": "2026-07-23T09:54:00.000Z"
}
```

### 🔍 명령 종류별 파라미터 규격 (`parameters` 구조)
1.  **긴급 정지 (`type: "stop"`)**:
    *   `parameters`: `{ "reason": "emergency" }` 또는 빈 객체. (기체는 즉시 제자리 호버링 또는 모터 정지 수행)
2.  **자동 복귀 (`type: "return"`)**:
    *   `parameters`: 빈 객체. (기체는 RTH 비행 경로를 계산하여 이륙 장소로 복귀)
3.  **일시 정지 / 재개 (`type: "pause"` / `type: "resume"`)**:
    *   임무 주행 경로 상의 제자리 일시 정지 및 비행 다시 시작.
4.  **원격 수동 조종 (`type: "manual_control"`)**:
    *   `parameters`: `{ "joystick_x": 0.8, "joystick_y": -0.3 }` (조이스틱 제어 방향 입력)

---

## 3. 기기 실행 결과 피드백 보고 (Command Acknowledgment)

기체는 서버로부터 2번 제어 명령(`command`)을 수신하고 실행에 들어가거나 완료/실패했을 때, 처리 경과를 아래 토픽으로 발행(Publish)하여 본부에 피드백을 전달해야 합니다.

*   **토픽 규격 (Topic)**:
    *   **드론 피드백**: `drone/{drone_id}/command/ack`
    *   **차량 피드백**: `vehicle/{vehicle_id}/command/ack`
*   **QoS 설정**: `1`

### 📋 JSON 메시지 규격 (Payload)
```json
{
  "command_id": "cmd-6e8fdb08-023d-419b-87de-2dcaa7a08ece",
  "status": "SUCCEEDED",
  "error_reason": null,
  "completed_at": "2026-07-23T09:54:05.120Z"
}
```

### 🔍 필드 설명 (Field Details)
*   `command_id`: 전달받은 명령 제어 고유 UUID와 반드시 **동일한 ID**를 맵핑하여 응답해야 합니다.
*   `status`: 처리 상태를 표시합니다.
    *   `RUNNING`: 명령을 수신하여 동작을 개시함.
    *   `SUCCEEDED`: 명령 수행을 성공적으로 완료함.
    *   `FAILED`: 장애나 유효하지 않은 동작으로 명령 수행에 실패함.
*   `error_reason`: `status`가 `FAILED`일 때, 기체 단말에서 발생한 에러 원인 문자열을 담습니다 (예: `"Hardware limit reached"`, `"No GPS signal"`).
*   `completed_at`: 명령 수행이 끝난 시각 (ISO 8601 UTC 표준 포맷).
