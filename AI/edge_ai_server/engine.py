"""Inference engine adapters.

The HTTP server never imports GPU libraries at module import time. This keeps
health checks and contract tests usable on developer machines and prevents a
failed model load from taking down unrelated process startup diagnostics.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import tempfile
import threading
from typing import Any, Mapping, Protocol, Sequence

from .config import Settings
from .models import BoundingBox, Detection


class InferenceError(RuntimeError):
    """Raised for model load or inference failures safe to expose to the API."""


class InferenceEngine(Protocol):
    @property
    def model_version(self) -> str: ...

    def infer(self, image_bytes: bytes) -> list[Detection]: ...

    def status(self) -> Mapping[str, Any]: ...


@dataclass(slots=True)
class MockInferenceEngine:
    """Deterministic engine used for integration tests without hardware."""

    detections: Sequence[Detection] = ()
    model_version: str = "mock-edge-ai-v1"

    def infer(self, image_bytes: bytes) -> list[Detection]:
        if not image_bytes:
            raise InferenceError("image payload is empty")
        return list(self.detections)

    def status(self) -> Mapping[str, Any]:
        return {
            "engine": "mock",
            "modelLoaded": True,
            "modelVersion": self.model_version,
            "hardwareControl": False,
        }


class UltralyticsInferenceEngine:
    """Single-flight Ultralytics adapter suitable for constrained Jetson GPU memory."""

    def __init__(
        self,
        model_path: str,
        model_version: str,
        device: str,
        image_size: int,
        confidence_threshold: float,
        class_map: Mapping[str, str],
    ) -> None:
        self._model_path = model_path
        self._model_version = model_version
        self._device = device
        self._image_size = image_size
        self._confidence_threshold = confidence_threshold
        self._class_map = {key.lower(): value for key, value in class_map.items()}
        self._model: Any = None
        self._load_error: str | None = None
        self._lock = threading.Lock()

    @property
    def model_version(self) -> str:
        return self._model_version

    def _load_model(self) -> Any:
        if self._model is not None:
            return self._model
        try:
            from ultralytics import YOLO  # type: ignore[import-not-found]

            model_path = Path(self._model_path)
            if not model_path.is_file():
                raise InferenceError(f"model file does not exist: {model_path}")
            self._model = YOLO(str(model_path))
            self._load_error = None
            return self._model
        except InferenceError:
            raise
        except Exception as exc:  # model libraries surface several runtime exception types
            self._load_error = str(exc)
            raise InferenceError(f"failed to load Ultralytics model: {exc}") from exc

    def infer(self, image_bytes: bytes) -> list[Detection]:
        if not image_bytes:
            raise InferenceError("image payload is empty")

        # A single lock prevents concurrent model calls from unexpectedly doubling
        # Jetson GPU memory usage. ThreadingHTTPServer may still serve health/status.
        with self._lock:
            model = self._load_model()
            temporary_path = ""
            try:
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as image_file:
                    image_file.write(image_bytes)
                    temporary_path = image_file.name
                results = model.predict(
                    source=temporary_path,
                    device=self._device,
                    imgsz=self._image_size,
                    conf=self._confidence_threshold,
                    verbose=False,
                )
                return self._convert_results(model, results)
            except InferenceError:
                raise
            except Exception as exc:
                raise InferenceError(f"model inference failed: {exc}") from exc
            finally:
                if temporary_path:
                    try:
                        os.unlink(temporary_path)
                    except FileNotFoundError:
                        pass

    def _convert_results(self, model: Any, results: Any) -> list[Detection]:
        detections: list[Detection] = []
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0].item())
                source_label = str(model.names[class_id]).lower()
                detection_type = self._class_map.get(source_label)
                if detection_type is None:
                    continue
                confidence = float(box.conf[0].item())
                x1, y1, x2, y2 = (float(value) for value in box.xyxy[0].tolist())
                detections.append(
                    Detection(
                        detection_type=detection_type,
                        confidence=confidence,
                        bounding_box=BoundingBox(
                            x=max(0, round(x1)),
                            y=max(0, round(y1)),
                            width=max(0, round(x2 - x1)),
                            height=max(0, round(y2 - y1)),
                        ),
                        source_label=source_label,
                    )
                )
        return detections

    def status(self) -> Mapping[str, Any]:
        return {
            "engine": "ultralytics",
            "modelLoaded": self._model is not None,
            "modelVersion": self._model_version,
            "modelPath": self._model_path,
            "device": self._device,
            "imageSize": self._image_size,
            "confidenceThreshold": self._confidence_threshold,
            "lastLoadError": self._load_error,
            "singleFlight": True,
            "hardwareControl": False,
        }


def build_engine(settings: Settings) -> InferenceEngine:
    if settings.engine == "mock":
        return MockInferenceEngine(model_version=settings.model_version)
    return UltralyticsInferenceEngine(
        model_path=settings.model_path,
        model_version=settings.model_version,
        device=settings.inference_device,
        image_size=settings.image_size,
        confidence_threshold=settings.confidence_threshold,
        class_map=settings.class_map or {},
    )

