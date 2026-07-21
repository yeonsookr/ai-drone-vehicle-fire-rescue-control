# 산불·조난 대응 드론·OrinCar 통합 관제 시스템

본 프로젝트는 드론과 지상 차량(OrinCar)을 활용한 산불 탐지 및 조난자 수색 통합 관제 시스템입니다.
현장의 드론 수집 데이터를 차량의 Jetson Orin이 On-Device AI로 1차 판단하고, 최종 데이터를 GPU 관제 서버를 거쳐 웹 플랫폼으로 전송하여 원격 제어 및 실시간 상태 관제를 구현합니다.

---

## 1. 프로젝트 폴더 구조 (Directory Structure)

본 프로젝트는 파트별 독립적 코딩과 협업을 원활하게 하기 위해 다음과 같은 구조로 세팅되어 있습니다. 모든 상세 설계 문서 및 규정 파일은 `docs/` 내부에서 관리합니다.

```text
C:\Users\SSAFY\ssafy_project_A302\S15P11A302\
├── AI/                    # Jetson Orin 엣지 AI 및 GPU 분석 알고리즘 소스
├── Server/                # 관제 메인 백엔드 서버 소스 (Java/Spring Boot)
├── Platform/              # 웹 실시간 관제 플랫폼 클라이언트 소스 (Vue.js)
├── docs/                  # 전체 시스템 문서
│   ├── images/            # 아키텍처 및 ERD 참조 이미지 폴더
│   ├── 기능명세서.md         # 통합 시스템 기능 명세서
│   ├── architecture_blueprint.md  # 아키텍처 구성 및 2구간 통신 흐름
│   ├── erd_design.md      # 관계형 데이터베이스(RDB) ERD 설계안
│   ├── exception_guidelines.md    # 파트별 예외 처리 및 Fail-safe 가이드라인
│   ├── git_guide.md       # Git 협업, 브랜치 명명 규칙 및 커밋 룰
│   └── AGENTS.md          # AI 개발 에이전트 전용 권한 규칙 및 검증 게이트
└── README.md              # 본 프로젝트 안내서 (유일한 루트 문서)
```

---

## 2. 파트별 개발 담당자 및 역할

| 역할 | 담당자 | 기본 책임 |
|---|---|---|
| **Embedded** | 윤주한 | 드론 내장 CPU·차량 Jetson Orin·차량 제어, 2구간(드론-차량-서버) 통신 중계 연동 및 안전 장치 구현 |
| **Backend** | 변준성 | GPU 메인 관제 서버, REST API, WebSocket 실시간 브로드캐스팅, 스케줄링 알고리즘 및 DB 설계 |
| **Platform** | 전우석 | 웹 실시간 관제 대시보드(지도, 영상, AI 결과 오버레이, 경보 알림, 긴급 제어 명령 UI) 개발 |
| **AI** | 장민규 | On-Device AI 모델 학습/최적화 및 배포, 서버 측 산불 확산 예측 모델 연동 개발 |
| **AI, SI & QA** | 박연수 | AI, 시스템 요구사항 설계 및 인터페이스 합의 조율, 통합 E2E 테스트 계획 수립 및 실행 제어 |

---

## 3. 핵심 아키텍처 및 협업 문서 바로가기

상세 설계 및 구현 가이드는 `docs/` 내부 문서를 참조하시기 바랍니다.

1. **[통합 기능 명세서](file:///C:/Users/SSAFY/ssafy_project_A302/S15P11A302/docs/기능명세서.md)**: 전체 시스템의 기능 ID 목록, 인수 기준 및 파트별 업무 배정표
2. **[아키텍처 Blueprint](file:///C:/Users/SSAFY/ssafy_project_A302/S15P11A302/docs/architecture_blueprint.md)**: MQTT 통신 기반의 2구간 통신 흐름 및 시퀀스 다이어그램
3. **[데이터베이스 ERD 설계안](file:///C:/Users/SSAFY/ssafy_project_A302/S15P11A302/docs/erd_design.md)**: 14개 물리 테이블의 상세 스키마 매핑 및 2구간 제어 추적 관계 설정
4. **[예외 처리 & 복구 가이드](file:///C:/Users/SSAFY/ssafy_project_A302/S15P11A302/docs/exception_guidelines.md)**: 기기 단절, 충돌 위험, 배터리 부족 시 Fail-safe 복구 시나리오
5. **[Git 사용 및 커밋 가이드](file:///C:/Users/SSAFY/ssafy_project_A302/S15P11A302/docs/git_guide.md)**: Git Flow 브랜치 전략, 커밋 메시지 컨벤션 및 PR 검토 프로세스
6. **[AI 에이전트 코딩 룰](file:///C:/Users/SSAFY/ssafy_project_A302/S15P11A302/docs/AGENTS.md)**: AI 코딩 어시스턴트 활용 시 준수해야 할 작업 경계 및 검증 게이트
