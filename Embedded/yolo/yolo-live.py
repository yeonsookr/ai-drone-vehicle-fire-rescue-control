import cv2
import torch
from flask import Flask, Response
from ultralytics import YOLO

# Flask 애플리케이션 설정
app = Flask(__name__)

# YOLOv8 모델 로드 및 CUDA 환경 설정
model = YOLO('yolov8n.pt')
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model.to(device)

# OpenCV에서 CUDA 사용 여부 확인
use_cuda = cv2.cuda.getCudaEnabledDeviceCount() > 0

# USB 카메라 연결 (/dev/video0)
cap = cv2.VideoCapture(0)

# 웹캠 해상도 및 FPS 설정
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 15)

def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            print("Error: Could not read frame.")
            break

        # 프레임 색상 변환 및 CUDA 가속 처리 적용
        if use_cuda:
            # 프레임을 GPU로 업로드하여 CUDA 가속 사용
            gpu_frame = cv2.cuda_GpuMat()
            gpu_frame.upload(frame)
            # CUDA에서 RGB로 변환
            gpu_frame_rgb = cv2.cuda.cvtColor(gpu_frame, cv2.COLOR_BGR2RGB)
            # GPU에서 CPU로 다시 다운로드
            frame_rgb = gpu_frame_rgb.download()
        else:
            # CUDA가 없는 경우 CPU에서 처리
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # YOLOv8 객체 감지 수행
        results = model(frame_rgb)

        # 다시 BGR로 변환 (OpenCV 처리를 위함)
        frame_processed = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        # 감지된 객체를 프레임에 사각형 및 텍스트로 표시
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                confidence = box.conf[0].item()
                class_id = box.cls[0].item()
                # class_id: 사물 이름 / confidence: 정확도
                label = f'{model.names[int(class_id)]}: {confidence:.2f}' 
                
                cv2.rectangle(frame_processed, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(frame_processed, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # 웹 스트리밍을 위해 JPEG 인코딩 및 바이트 변환
        ret, buffer = cv2.imencode('.jpg', frame_processed)
        frame_bytes = buffer.tobytes()
        
        # MJPEG 스트림 형식으로 yield
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video')
def video_feed():
    # 처리된 프레임을 multipart 형식의 Response 객체로 반환
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # 0.0.0.0으로 열어 외부 접속 허용 (포트: 5000)
    app.run(host='0.0.0.0', port=5000, debug=False)