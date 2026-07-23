"""HTTP client for publishing Jetson AI results to the Spring backend."""

from __future__ import annotations

from dataclasses import dataclass
import json
import time
from typing import Any, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4

from .models import Detection, InferenceRequest


class BackendClientError(RuntimeError):
    """Backend transport or non-success response error."""


def encode_multipart(
    fields: Mapping[str, str],
    files: Iterable[tuple[str, str, str, bytes]],
) -> tuple[bytes, str]:
    """Encode multipart/form-data without adding a requests dependency."""
    boundary = f"edge-ai-{uuid4().hex}"
    body = bytearray()

    def append_line(value: str | bytes = b"") -> None:
        body.extend(value.encode("utf-8") if isinstance(value, str) else value)
        body.extend(b"\r\n")

    for name, value in fields.items():
        append_line(f"--{boundary}")
        append_line(f'Content-Disposition: form-data; name="{name}"')
        append_line("Content-Type: text/plain; charset=utf-8")
        append_line()
        append_line(value)

    for field_name, filename, content_type, content in files:
        safe_filename = filename.replace('"', "")
        append_line(f"--{boundary}")
        append_line(
            f'Content-Disposition: form-data; name="{field_name}"; filename="{safe_filename}"'
        )
        append_line(f"Content-Type: {content_type}")
        append_line()
        body.extend(content)
        body.extend(b"\r\n")

    append_line(f"--{boundary}--")
    return bytes(body), f"multipart/form-data; boundary={boundary}"


@dataclass(frozen=True, slots=True)
class PublishResponse:
    detection_index: int
    status_code: int
    body: Mapping[str, Any]


class CentralBackendClient:
    def __init__(
        self,
        base_url: str,
        token: str = "",
        timeout_seconds: float = 5.0,
        attempts: int = 3,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._token = token
        self._timeout_seconds = timeout_seconds
        self._attempts = attempts

    @property
    def enabled(self) -> bool:
        return bool(self._base_url)

    def publish_detections(
        self,
        request: InferenceRequest,
        detections: list[Detection],
        image_bytes: bytes,
        model_version: str,
        image_content_type: str = "image/jpeg",
    ) -> list[PublishResponse]:
        responses: list[PublishResponse] = []
        extension = ".png" if image_content_type == "image/png" else ".jpg"
        for index, detection in enumerate(detections):
            metadata = {
                "missionId": request.mission_id,
                "deviceId": request.device_id,
                "deviceType": "vehicle",
                "detectionType": detection.detection_type,
                "confidence": detection.confidence,
                "boundingBox": detection.bounding_box.to_dict(),
                "latitude": request.latitude,
                "longitude": request.longitude,
                "altitude": request.altitude,
                "detectedAt": request.captured_at,
                "modelVersion": model_version,
                "source": "edge_ai_orin",
            }
            body, content_type = encode_multipart(
                {"metadata": json.dumps(metadata, ensure_ascii=False, separators=(",", ":"))},
                [("file", f"{request.request_id}{extension}", image_content_type, image_bytes)],
            )
            response_code, response_body = self._send_with_retry(
                path="/api/detections/snapshot",
                body=body,
                content_type=content_type,
                idempotency_key=f"{request.request_id}:{index}",
            )
            responses.append(PublishResponse(index, response_code, response_body))
        return responses

    def register_video_stream(
        self,
        device_id: str,
        stream_url: str,
        status: str,
        mission_id: str | None = None,
    ) -> Mapping[str, Any]:
        payload = {
            "deviceId": device_id,
            "deviceType": "vehicle",
            "streamUrl": stream_url,
            "status": status,
            "missionId": mission_id,
        }
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        _, response = self._send_with_retry(
            path="/api/video-streams",
            body=body,
            content_type="application/json",
            idempotency_key=f"stream:{device_id}",
        )
        return response

    def _send_with_retry(
        self,
        path: str,
        body: bytes,
        content_type: str,
        idempotency_key: str,
    ) -> tuple[int, Mapping[str, Any]]:
        if not self.enabled:
            raise BackendClientError("backend publishing is disabled")
        last_error: Exception | None = None
        for attempt in range(1, self._attempts + 1):
            headers = {
                "Content-Type": content_type,
                "Accept": "application/json",
                "X-Idempotency-Key": idempotency_key,
                "User-Agent": "jetson-edge-ai/0.3",
            }
            if self._token:
                headers["Authorization"] = f"Bearer {self._token}"
            request = Request(
                f"{self._base_url}{path}",
                data=body,
                headers=headers,
                method="POST",
            )
            try:
                with urlopen(request, timeout=self._timeout_seconds) as response:
                    response_bytes = response.read()
                    parsed = json.loads(response_bytes.decode("utf-8")) if response_bytes else {}
                    return response.status, parsed
            except HTTPError as exc:
                response_bytes = exc.read()
                message = response_bytes.decode("utf-8", errors="replace")
                # Retry only transient server failures; validation failures must not loop.
                if exc.code < 500 or attempt == self._attempts:
                    raise BackendClientError(f"backend returned HTTP {exc.code}: {message}") from exc
                last_error = exc
            except (URLError, TimeoutError, OSError) as exc:
                last_error = exc
                if attempt == self._attempts:
                    break
            time.sleep(min(0.25 * (2 ** (attempt - 1)), 1.0))
        raise BackendClientError(f"backend request failed after {self._attempts} attempts: {last_error}")
