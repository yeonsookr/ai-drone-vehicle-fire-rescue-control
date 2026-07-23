"""Build a device-specific TensorRT FP16 engine on the target Jetson Orin."""

from pathlib import Path

import yaml
from ultralytics import YOLO


BASE_DIR = Path(__file__).resolve().parent


def main() -> None:
    with (BASE_DIR / "config.yaml").open(encoding="utf-8") as file:
        config = yaml.safe_load(file)

    model = YOLO(str(BASE_DIR / config["model"]), task="detect")
    output = model.export(
        format="engine",
        imgsz=int(config["imgsz"]),
        batch=1,
        device=0,
        quantize=16,
    )
    print(f"TensorRT engine created: {output}")


if __name__ == "__main__":
    main()
