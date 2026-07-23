"""Environment based configuration for the edge AI server."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Mapping


def _as_bool(value: str | bool | None, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"invalid boolean value: {value!r}")


def _read_dotenv(path: Path) -> dict[str, str]:
    """Read a small, dependency-free subset of the dotenv format."""
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            raise ValueError(f"invalid .env line {line_number}: expected KEY=VALUE")
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values[key] = value
    return values


@dataclass(frozen=True, slots=True)
class Settings:
    host: str = "127.0.0.1"
    port: int = 5001
    api_token: str = ""
    allow_insecure_remote: bool = False

    backend_base_url: str = "http://127.0.0.1:8080"
    backend_token: str = ""
    backend_timeout_seconds: float = 5.0
    backend_publish_enabled: bool = True
    backend_publish_attempts: int = 3

    mqtt_enabled: bool = False
    mqtt_host: str = "127.0.0.1"
    mqtt_port: int = 1883
    mqtt_client_id: str = "jetson-edge-ai"
    mqtt_username: str = ""
    mqtt_password: str = ""
    mqtt_tls_enabled: bool = False
    mqtt_keepalive_seconds: int = 30
    mqtt_qos: int = 1
    mqtt_status_interval_seconds: float = 10.0
    mqtt_command_default_ttl_seconds: int = 30

    vehicle_id: str = "V-01"
    engine: str = "mock"
    model_path: str = ""
    model_version: str = "edge-ai-unconfigured"
    inference_device: str = "cuda:0"
    image_size: int = 640
    confidence_threshold: float = 0.25
    review_threshold: float = 0.5
    class_map: Mapping[str, str] | None = None

    max_request_bytes: int = 10 * 1024 * 1024
    result_cache_size: int = 256
    publish_queue_size: int = 128
    frame_queue_size: int = 8
    frame_buffer_size: int = 60
    evidence_frame_count: int = 3
    evidence_window_seconds: float = 10.0
    event_cooldown_seconds: float = 30.0
    command_cache_size: int = 128

    @classmethod
    def from_env(
        cls,
        environ: Mapping[str, str] | None = None,
        dotenv_path: Path | None = None,
    ) -> "Settings":
        source = dict(_read_dotenv(dotenv_path or Path.cwd() / ".env"))
        source.update(dict(os.environ if environ is None else environ))

        raw_class_map = source.get("EDGE_AI_CLASS_MAP_JSON", "")
        if raw_class_map:
            parsed_class_map = json.loads(raw_class_map)
            if not isinstance(parsed_class_map, dict):
                raise ValueError("EDGE_AI_CLASS_MAP_JSON must be a JSON object")
            class_map = {str(key).lower(): str(value) for key, value in parsed_class_map.items()}
        else:
            class_map = {
                "fire": "forest_fire",
                "flame": "forest_fire",
                "forest_fire": "forest_fire",
                "wildfire": "forest_fire",
                "smoke": "smoke",
                "person": "distressed_person",
                "distressed_person": "distressed_person",
            }

        settings = cls(
            host=source.get("EDGE_AI_HOST", "127.0.0.1"),
            port=int(source.get("EDGE_AI_PORT", "5001")),
            api_token=source.get("EDGE_AI_API_TOKEN", ""),
            allow_insecure_remote=_as_bool(source.get("EDGE_AI_ALLOW_INSECURE_REMOTE"), False),
            backend_base_url=source.get("BACKEND_BASE_URL", "http://127.0.0.1:8080").rstrip("/"),
            backend_token=source.get("BACKEND_API_TOKEN", ""),
            backend_timeout_seconds=float(source.get("BACKEND_TIMEOUT_SECONDS", "5")),
            backend_publish_enabled=_as_bool(source.get("BACKEND_PUBLISH_ENABLED"), True),
            backend_publish_attempts=int(source.get("BACKEND_PUBLISH_ATTEMPTS", "3")),
            mqtt_enabled=_as_bool(source.get("MQTT_ENABLED"), False),
            mqtt_host=source.get("MQTT_HOST", "127.0.0.1"),
            mqtt_port=int(source.get("MQTT_PORT", "1883")),
            mqtt_client_id=source.get("MQTT_CLIENT_ID", "jetson-edge-ai"),
            mqtt_username=source.get("MQTT_USERNAME", ""),
            mqtt_password=source.get("MQTT_PASSWORD", ""),
            mqtt_tls_enabled=_as_bool(source.get("MQTT_TLS_ENABLED"), False),
            mqtt_keepalive_seconds=int(source.get("MQTT_KEEPALIVE_SECONDS", "30")),
            mqtt_qos=int(source.get("MQTT_QOS", "1")),
            mqtt_status_interval_seconds=float(source.get("MQTT_STATUS_INTERVAL_SECONDS", "10")),
            mqtt_command_default_ttl_seconds=int(
                source.get("MQTT_COMMAND_DEFAULT_TTL_SECONDS", "30")
            ),
            vehicle_id=source.get("EDGE_VEHICLE_ID", "V-01"),
            engine=source.get("EDGE_AI_ENGINE", "mock").lower(),
            model_path=source.get("EDGE_AI_MODEL_PATH", ""),
            model_version=source.get("EDGE_AI_MODEL_VERSION", "edge-ai-unconfigured"),
            inference_device=source.get("EDGE_AI_DEVICE", "cuda:0"),
            image_size=int(source.get("EDGE_AI_IMAGE_SIZE", "640")),
            confidence_threshold=float(source.get("EDGE_AI_CONFIDENCE_THRESHOLD", "0.25")),
            review_threshold=float(source.get("EDGE_AI_REVIEW_THRESHOLD", "0.5")),
            class_map=class_map,
            max_request_bytes=int(source.get("EDGE_AI_MAX_REQUEST_BYTES", str(10 * 1024 * 1024))),
            result_cache_size=int(source.get("EDGE_AI_RESULT_CACHE_SIZE", "256")),
            publish_queue_size=int(source.get("EDGE_AI_PUBLISH_QUEUE_SIZE", "128")),
            frame_queue_size=int(source.get("EDGE_AI_FRAME_QUEUE_SIZE", "8")),
            frame_buffer_size=int(source.get("EDGE_AI_FRAME_BUFFER_SIZE", "60")),
            evidence_frame_count=int(source.get("EDGE_AI_EVIDENCE_FRAME_COUNT", "3")),
            evidence_window_seconds=float(source.get("EDGE_AI_EVIDENCE_WINDOW_SECONDS", "10")),
            event_cooldown_seconds=float(source.get("EDGE_AI_EVENT_COOLDOWN_SECONDS", "30")),
            command_cache_size=int(source.get("EDGE_AI_COMMAND_CACHE_SIZE", "128")),
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        if not 1 <= self.port <= 65535:
            raise ValueError("EDGE_AI_PORT must be between 1 and 65535")
        if self.host not in {"127.0.0.1", "localhost", "::1"}:
            if not self.api_token and not self.allow_insecure_remote:
                raise ValueError(
                    "EDGE_AI_API_TOKEN is required when binding to a non-loopback address; "
                    "set EDGE_AI_ALLOW_INSECURE_REMOTE=true only in an isolated test network"
                )
        if self.engine not in {"mock", "ultralytics"}:
            raise ValueError("EDGE_AI_ENGINE must be 'mock' or 'ultralytics'")
        if self.engine == "ultralytics" and not self.model_path:
            raise ValueError("EDGE_AI_MODEL_PATH is required for the ultralytics engine")
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError("EDGE_AI_CONFIDENCE_THRESHOLD must be between 0 and 1")
        if not 0.0 <= self.review_threshold <= 1.0:
            raise ValueError("EDGE_AI_REVIEW_THRESHOLD must be between 0 and 1")
        if self.review_threshold < self.confidence_threshold:
            raise ValueError("EDGE_AI_REVIEW_THRESHOLD cannot be below the confidence threshold")
        if self.max_request_bytes <= 0:
            raise ValueError("EDGE_AI_MAX_REQUEST_BYTES must be positive")
        if self.result_cache_size <= 0 or self.publish_queue_size <= 0:
            raise ValueError("cache and publish queue sizes must be positive")
        if self.frame_queue_size <= 0 or self.frame_buffer_size <= 0:
            raise ValueError("frame queue and buffer sizes must be positive")
        if self.evidence_frame_count <= 0 or self.evidence_frame_count > 20:
            raise ValueError("EDGE_AI_EVIDENCE_FRAME_COUNT must be between 1 and 20")
        if self.evidence_window_seconds <= 0 or self.event_cooldown_seconds < 0:
            raise ValueError("evidence window must be positive and cooldown cannot be negative")
        if self.command_cache_size <= 0:
            raise ValueError("EDGE_AI_COMMAND_CACHE_SIZE must be positive")
        if self.backend_publish_attempts <= 0:
            raise ValueError("BACKEND_PUBLISH_ATTEMPTS must be positive")
        if self.mqtt_enabled and not self.mqtt_host.strip():
            raise ValueError("MQTT_HOST is required when MQTT is enabled")
        if not 1 <= self.mqtt_port <= 65535:
            raise ValueError("MQTT_PORT must be between 1 and 65535")
        if self.mqtt_qos not in {0, 1, 2}:
            raise ValueError("MQTT_QOS must be 0, 1, or 2")
        if self.mqtt_keepalive_seconds <= 0 or self.mqtt_status_interval_seconds <= 0:
            raise ValueError("MQTT keepalive and status interval must be positive")
        if self.mqtt_command_default_ttl_seconds <= 0:
            raise ValueError("MQTT_COMMAND_DEFAULT_TTL_SECONDS must be positive")
