"""Validated domain models shared by the HTTP and inference layers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import math
from typing import Any, Mapping


ALLOWED_DETECTION_TYPES = {"forest_fire", "smoke", "distressed_person"}
ALLOWED_JUDGMENTS = {"approved", "false_alarm", "pending"}
ALLOWED_COMMAND_TYPES = {"capture", "burst_capture", "reanalyze"}


class ValidationError(ValueError):
    """Raised when an API payload does not satisfy the edge contract."""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _get(data: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in data:
            return data[key]
    return default


def _required_text(data: Mapping[str, Any], *keys: str) -> str:
    value = _get(data, *keys)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{keys[0]} is required")
    return value.strip()


def _finite_float(data: Mapping[str, Any], *keys: str, default: float | None = None) -> float:
    value = _get(data, *keys, default=default)
    if value is None:
        raise ValidationError(f"{keys[0]} is required")
    if isinstance(value, bool):
        raise ValidationError(f"{keys[0]} must be a number")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{keys[0]} must be a number") from exc
    if not math.isfinite(parsed):
        raise ValidationError(f"{keys[0]} must be finite")
    return parsed


def normalize_local_datetime(value: str) -> str:
    """Validate ISO-8601 and return a Spring LocalDateTime compatible value."""
    if not isinstance(value, str) or not value.strip():
        raise ValidationError("capturedAt is required")
    normalized = value.strip()
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError("capturedAt must be ISO-8601") from exc
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed.isoformat(timespec="milliseconds")


@dataclass(frozen=True, slots=True)
class InferenceRequest:
    request_id: str
    mission_id: str | None
    device_id: str
    captured_at: str
    latitude: float
    longitude: float
    altitude: float
    auto_publish: bool
    source_drone_id: str | None = None

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any], default_device_id: str) -> "InferenceRequest":
        request_id = _required_text(data, "requestId", "request_id")
        mission_value = _get(data, "missionId", "mission_id")
        mission_id = str(mission_value).strip() if mission_value is not None else None
        if mission_id == "":
            mission_id = None
        device_value = _get(data, "deviceId", "device_id", default=default_device_id)
        if not isinstance(device_value, str) or not device_value.strip():
            raise ValidationError("deviceId is required")
        latitude = _finite_float(data, "latitude")
        longitude = _finite_float(data, "longitude")
        altitude = _finite_float(data, "altitude", default=0.0)
        if not -90.0 <= latitude <= 90.0:
            raise ValidationError("latitude must be between -90 and 90")
        if not -180.0 <= longitude <= 180.0:
            raise ValidationError("longitude must be between -180 and 180")
        if not -500.0 <= altitude <= 20_000.0:
            raise ValidationError("altitude is outside the accepted range")
        auto_publish_raw = _get(data, "autoPublish", "auto_publish", default=True)
        if not isinstance(auto_publish_raw, bool):
            raise ValidationError("autoPublish must be a boolean")
        return cls(
            request_id=request_id,
            mission_id=mission_id,
            device_id=device_value.strip(),
            captured_at=normalize_local_datetime(_required_text(data, "capturedAt", "captured_at")),
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
            auto_publish=auto_publish_raw,
            source_drone_id=None,
        )


@dataclass(frozen=True, slots=True)
class FrameMetadata:
    frame_id: str
    mission_id: str | None
    source_drone_id: str
    captured_at: str
    latitude: float
    longitude: float
    altitude: float

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "FrameMetadata":
        frame_id = _required_text(data, "frameId", "frame_id")
        mission_value = _get(data, "missionId", "mission_id")
        mission_id = str(mission_value).strip() if mission_value else None
        source_drone_id = _required_text(data, "sourceDroneId", "source_drone_id", "droneId")
        latitude = _finite_float(data, "latitude")
        longitude = _finite_float(data, "longitude")
        altitude = _finite_float(data, "altitude", default=0.0)
        if not -90.0 <= latitude <= 90.0:
            raise ValidationError("latitude must be between -90 and 90")
        if not -180.0 <= longitude <= 180.0:
            raise ValidationError("longitude must be between -180 and 180")
        if not -500.0 <= altitude <= 20_000.0:
            raise ValidationError("altitude is outside the accepted range")
        return cls(
            frame_id=frame_id,
            mission_id=mission_id,
            source_drone_id=source_drone_id,
            captured_at=normalize_local_datetime(_required_text(data, "capturedAt", "captured_at")),
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
        )

    def to_inference_request(self, vehicle_id: str, request_id: str | None = None) -> InferenceRequest:
        return InferenceRequest(
            request_id=request_id or self.frame_id,
            mission_id=self.mission_id,
            device_id=vehicle_id,
            captured_at=self.captured_at,
            latitude=self.latitude,
            longitude=self.longitude,
            altitude=self.altitude,
            auto_publish=False,
            source_drone_id=self.source_drone_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "frameId": self.frame_id,
            "missionId": self.mission_id,
            "sourceDroneId": self.source_drone_id,
            "capturedAt": self.captured_at,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
        }


@dataclass(frozen=True, slots=True)
class BoundingBox:
    x: int
    y: int
    width: int
    height: int

    def to_dict(self) -> dict[str, int]:
        return {"x": self.x, "y": self.y, "w": self.width, "h": self.height}


@dataclass(frozen=True, slots=True)
class Detection:
    detection_type: str
    confidence: float
    bounding_box: BoundingBox
    source_label: str = ""

    def __post_init__(self) -> None:
        if self.detection_type not in ALLOWED_DETECTION_TYPES:
            raise ValidationError(f"unsupported detection type: {self.detection_type}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValidationError("confidence must be between 0 and 1")

    def to_dict(self, review_threshold: float) -> dict[str, Any]:
        return {
            "detectionType": self.detection_type,
            "confidence": round(self.confidence, 6),
            "boundingBox": self.bounding_box.to_dict(),
            "sourceLabel": self.source_label,
            "operatorAction": "review_required" if self.confidence < review_threshold else "confirm_required",
        }


@dataclass(frozen=True, slots=True)
class OperatorFeedback:
    request_id: str
    event_id: str | None
    judgment: str
    reason: str | None
    judged_at: str

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "OperatorFeedback":
        request_id = _required_text(data, "requestId", "request_id")
        judgment = _required_text(data, "judgment").lower()
        if judgment not in ALLOWED_JUDGMENTS:
            raise ValidationError(f"judgment must be one of {sorted(ALLOWED_JUDGMENTS)}")
        event_value = _get(data, "eventId", "event_id")
        reason_value = _get(data, "reason")
        judged_value = _get(data, "judgedAt", "judged_at", default=utc_now_iso())
        return cls(
            request_id=request_id,
            event_id=str(event_value).strip() if event_value else None,
            judgment=judgment,
            reason=str(reason_value).strip() if reason_value else None,
            judged_at=normalize_local_datetime(str(judged_value)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "requestId": self.request_id,
            "eventId": self.event_id,
            "judgment": self.judgment,
            "reason": self.reason,
            "judgedAt": self.judged_at,
        }


@dataclass(frozen=True, slots=True)
class BackendCommand:
    command_id: str
    command_type: str
    target_id: str
    issued_at: str
    expires_at: str
    parameters: Mapping[str, Any]

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "BackendCommand":
        command_type = _required_text(data, "type").lower()
        if command_type not in ALLOWED_COMMAND_TYPES:
            raise ValidationError(f"type must be one of {sorted(ALLOWED_COMMAND_TYPES)}")
        parameters = _get(data, "parameters", default={})
        if not isinstance(parameters, dict):
            raise ValidationError("parameters must be an object")
        return cls(
            command_id=_required_text(data, "commandId", "command_id"),
            command_type=command_type,
            target_id=_required_text(data, "targetId", "target_id"),
            issued_at=normalize_local_datetime(_required_text(data, "issuedAt", "issued_at")),
            expires_at=normalize_local_datetime(_required_text(data, "expiresAt", "expires_at")),
            parameters=parameters,
        )

    def requested_frame_count(self) -> int:
        if self.command_type == "capture":
            return 1
        if self.command_type == "reanalyze":
            return 1
        raw_count = self.parameters.get("count", 3)
        if isinstance(raw_count, bool):
            raise ValidationError("parameters.count must be an integer")
        try:
            count = int(raw_count)
        except (TypeError, ValueError) as exc:
            raise ValidationError("parameters.count must be an integer") from exc
        if not 1 <= count <= 10:
            raise ValidationError("parameters.count must be between 1 and 10")
        return count

    def fingerprint(self) -> str:
        import json

        return json.dumps(
            {
                "type": self.command_type,
                "targetId": self.target_id,
                "issuedAt": self.issued_at,
                "expiresAt": self.expires_at,
                "parameters": self.parameters,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
