# 한국 산불 데이터 YOLO26n 전처리·학습 가이드

## 1. 적용 범위

- 선별된 AI Hub Training 이미지 전체를 `train`으로 사용한다.
- AI Hub에서 제공한 Validation을 Ultralytics의 `val` 원천으로 사용한다.
- Training과 같은 촬영 시퀀스가 Validation에도 있으면 평가 누수를 막기 위해 해당 Validation 이미지만 제외한다. 선별 Training을 다시 나누지는 않는다.
- 모델 클래스는 기존 AI 브랜치의 표현과 맞춰 `0: fire`, `1: smoke`로 고정한다.
- 운영 API로 전송할 때 `fire`를 `forest_fire` 이벤트로 변환한다.
- 기존 `AI/SAM3.1_init` 노트북과 결과 파일은 수정하지 않는다.

원본 클래스 매핑은 다음과 같다.

| AI Hub 클래스 | 모델 클래스 | 처리 방식 |
|---|---|---|
| 화염 | `fire` (`0`) | 객체 박스 유지 |
| 흑색연기 | `smoke` (`1`) | 객체 박스 유지 |
| 백색/회색연기 | `smoke` (`1`) | 객체 박스 유지 |
| 구름 | 없음 | 이미지 유지, 해당 박스 제거 |
| 안개/연무 | 없음 | 이미지 유지, 해당 박스 제거 |
| 굴뚝연기 | 없음 | 이미지 유지, 해당 박스 제거 |

구름·안개/연무·굴뚝연기 이미지는 빈 YOLO 라벨을 가진 Hard Negative로 학습한다.

## 2. 사전 조건

`ultralytics`와 `Pillow`가 필요하다. 저장소 정책에 따라 의존성 설치 또는 버전 변경은 팀에 알리고 승인된 AI 환경에서 수행한다. 이 작업에서는 패키지 설치와 `requirements.txt` 변경을 수행하지 않는다.

Ultralytics 배포 라이선스는 AGPL-3.0 또는 Enterprise 조건을 확인해야 한다.

## 3. 전처리

먼저 파일을 만들지 않는 검증을 실행한다.

```powershell
python AI/yolo26/preprocess_aihub.py `
  --train-images "C:\Users\SSAFY\Desktop\MVP전처리학습\2차 선별 데이터(학습용)" `
  --train-labels "C:\Users\SSAFY\Desktop\MVP전처리학습\2차 선별 데이터(학습용)\02.라벨링데이터" `
  --val-images "C:\Users\SSAFY\Desktop\MVP전처리학습\Validation\01.원천데이터\VS" `
  --val-labels "C:\Users\SSAFY\Desktop\MVP전처리학습\Validation\02.라벨링데이터\VL" `
  --output-dir "C:\Users\SSAFY\Desktop\MVP전처리학습\yolo26_kr_dataset" `
  --dry-run
```

누락·중복 라벨, 손상 이미지, 이미지 크기 불일치, 범위를 벗어난 박스와 미정의 클래스가 있으면 중단된다. Training/Validation의 촬영 시퀀스가 겹치면 기본값인 `--val-overlap-policy exclude`가 겹치는 Validation 이미지만 제외한다. 엄격히 중단하려면 `--val-overlap-policy error`를 사용한다.

현재 데이터 전수 검사에서는 Training 2,022장을 전부 유지하고, 공식 Validation 69,635장 중 같은 촬영 시퀀스의 26,606장을 제외하여 43,029장을 `val`로 사용한다. 제외 수와 예시는 `reports/preprocess_report.json`의 `cross_split`에 기록된다.

검증을 통과하면 `--dry-run`만 제거해 실제 데이터셋을 만든다.

```powershell
python AI/yolo26/preprocess_aihub.py `
  --train-images "C:\Users\SSAFY\Desktop\MVP전처리학습\2차 선별 데이터(학습용)" `
  --train-labels "C:\Users\SSAFY\Desktop\MVP전처리학습\2차 선별 데이터(학습용)\02.라벨링데이터" `
  --val-images "C:\Users\SSAFY\Desktop\MVP전처리학습\Validation\01.원천데이터\VS" `
  --val-labels "C:\Users\SSAFY\Desktop\MVP전처리학습\Validation\02.라벨링데이터\VL" `
  --output-dir "C:\Users\SSAFY\Desktop\MVP전처리학습\yolo26_kr_dataset"
```

기본값은 원본 보호를 위해 이미지를 복사한다. 같은 드라이브에서 저장 공간을 줄이려면 `--mode hardlink`를 명시할 수 있지만, 하드링크 파일 내용 변경은 원본에도 영향을 주므로 데이터셋 파일을 수정하면 안 된다.

생성 결과:

```text
yolo26_kr_dataset/
├── data.yaml
├── images/
│   ├── train/
│   └── val/
├── labels/
│   ├── train/
│   └── val/
└── reports/
    ├── manifest.csv
    ├── preprocess_report.json
    └── visualizations/
```

학습 전 `reports/visualizations`의 박스와 Hard Negative 표시를 사람이 확인한다.

## 4. YOLO26n 학습

```powershell
python AI/yolo26/train_yolo26.py `
  --data "C:\Users\SSAFY\Desktop\MVP전처리학습\yolo26_kr_dataset\data.yaml" `
  --model yolo26n.pt `
  --epochs 100 `
  --imgsz 640 `
  --batch 0.70 `
  --device 0 `
  --workers 4 `
  --project-dir "C:\Users\SSAFY\Desktop\MVP전처리학습\yolo26_runs" `
  --name kr_yolo26n_baseline
```

`batch=0.70`은 단일 GPU 메모리의 약 70%를 목표로 자동 배치를 선택한다. 메모리 문제가 있으면 `--batch 8`처럼 고정값을 사용한다.

학습 결과 폴더에는 `best.pt`, `last.pt`, 학습 곡선, Confusion Matrix, PR Curve와 `validation_summary.json`이 저장된다.

중단된 학습은 다음과 같이 이어간다.

```powershell
python AI/yolo26/train_yolo26.py `
  --data "C:\Users\SSAFY\Desktop\MVP전처리학습\yolo26_kr_dataset\data.yaml" `
  --resume "C:\path\to\last.pt"
```

## 5. 결과 해석

현재 Validation을 반복적으로 확인하며 모델 설정을 조정하므로 결과는 `AI Hub Validation 성능`으로 기록한다. 독립적인 최종 Test 성능으로 표현하지 않는다.

확인 지표:

- `mAP@0.5:0.95`, `mAP@0.5`
- `fire`, `smoke` 클래스별 AP
- Precision과 Recall
- Hard Negative의 False Positive
- 원거리·야간·저대비 이미지 예측 결과
- 실제 Jetson Orin 환경의 FPS, 지연과 메모리 사용량
