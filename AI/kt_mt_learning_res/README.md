# 0723 KT/MT Jetson Orin 전달 패키지

산불 화염(`fire`)과 연기(`smoke`)를 탐지하도록 학습한 YOLO26n 모델의
Jetson Orin 배포 패키지입니다.

## 구성

- `best.pt`: 최종 추론용 PyTorch 모델
- `detect.py`: 카메라·영상·스트림 추론 코드
- `config.yaml`: 모델, 입력 크기, 임계값 및 클래스 매핑
- `export_tensorrt.py`: Jetson에서 FP16 TensorRT 엔진 생성
- `requirements.txt`: Python 의존성
- `MODEL_INFO.json`: 모델 버전, 성능, 체크섬
- `training_metadata/`: 학습·검증·테스트 기록

학습 데이터, `last.pt`, 학습 코드 및 Windows 가상환경은 포함하지 않았습니다.

## Jetson 실행

JetPack 버전에 맞는 PyTorch와 Torchvision을 먼저 설치한 뒤 나머지 패키지를
설치합니다.

```bash
python3 -m pip install -r requirements.txt
```

먼저 PyTorch 모델로 카메라 추론을 확인합니다.

```bash
python3 detect.py --source 0
```

화면 없이 실행하려면 다음과 같이 사용합니다.

```bash
python3 detect.py --source 0 --no-display
```

영상 파일이나 RTSP 주소도 `--source`에 지정할 수 있습니다.

## TensorRT 변환

TensorRT 엔진은 대상 Jetson의 GPU, CUDA, TensorRT 및 JetPack 환경에
의존하므로 반드시 실제로 사용할 Jetson에서 생성합니다.

```bash
python3 export_tensorrt.py
```

`best.engine`이 생성되면 `detect.py`가 `.pt` 대신 엔진을 자동으로 사용합니다.

## 운영 참고

- 학습 입력 크기: `1280`
- 기본 confidence: `0.25`
- 모델 출력 `fire`는 운영 이벤트 `forest_fire`로 변환
- smoke의 테스트 AP가 fire보다 낮으므로 실제 카메라 환경에서 임계값 조정 및
  추가 검증 필요
