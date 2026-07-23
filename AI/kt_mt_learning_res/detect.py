"""Jetson Orin camera/video inference for the trained fire and smoke model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import yaml
from ultralytics import YOLO


BASE_DIR = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(BASE_DIR / "config.yaml"))
    parser.add_argument("--source", help="Camera index, video path, or stream URL")
    parser.add_argument("--model", help="Override the model path")
    parser.add_argument("--no-display", action="store_true")
    return parser.parse_args()


def resolve_source(value: object) -> int | str:
    text = str(value)
    return int(text) if text.isdigit() else text


def resolve_model(config: dict, override: str | None) -> Path:
    if override:
        path = Path(override)
        return path if path.is_absolute() else BASE_DIR / path

    engine_path = BASE_DIR / config["engine"]
    if engine_path.exists():
        return engine_path
    return BASE_DIR / config["model"]


def main() -> None:
    args = parse_args()
    with Path(args.config).open(encoding="utf-8") as file:
        config = yaml.safe_load(file)

    model_path = resolve_model(config, args.model)
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    source = resolve_source(args.source if args.source is not None else config["source"])
    model = YOLO(str(model_path), task="detect")
    capture = cv2.VideoCapture(source)
    if not capture.isOpened():
        raise RuntimeError(f"Could not open source: {source}")

    event_mapping = config["event_type_mapping"]

    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break

            result = model.predict(
                frame,
                imgsz=int(config["imgsz"]),
                conf=float(config["confidence"]),
                iou=float(config["iou"]),
                device=config["device"],
                verbose=False,
            )[0]

            detections = []
            for box in result.boxes:
                class_id = int(box.cls[0])
                class_name = model.names[class_id]
                x1, y1, x2, y2 = (round(value, 2) for value in box.xyxy[0].tolist())
                detections.append(
                    {
                        "detection_type": event_mapping[class_name],
                        "class_name": class_name,
                        "confidence": round(float(box.conf[0]), 4),
                        "bounding_box_xyxy": [x1, y1, x2, y2],
                    }
                )

            if detections:
                print(json.dumps(detections, ensure_ascii=False), flush=True)

            if not args.no_display:
                cv2.imshow("Fire/Smoke Detection", result.plot())
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    finally:
        capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
