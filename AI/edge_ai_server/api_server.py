"""Dependency-free threaded HTTP API for the Jetson edge AI service."""

from __future__ import annotations

import base64
import binascii
from email.parser import BytesParser
from email.policy import default as email_policy
import hmac
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
from typing import Any, Mapping
from urllib.parse import unquote, urlparse

from .backend_client import CentralBackendClient
from .config import Settings
from .engine import InferenceError, build_engine
from .models import FrameMetadata, ValidationError, utc_now_iso
from .pipeline import ContinuousInferencePipeline, PipelineBusyError
from .service import (
    ConflictError,
    EdgeAiService,
    PublishQueueFullError,
    ResourceNotFoundError,
)


LOGGER = logging.getLogger("edge_ai_server.http")


class RequestError(ValueError):
    def __init__(self, status: HTTPStatus, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


class EdgeAiHttpServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(
        self,
        address: tuple[str, int],
        settings: Settings,
        service: EdgeAiService,
        pipeline: ContinuousInferencePipeline,
    ) -> None:
        self.settings = settings
        self.service = service
        self.pipeline = pipeline
        self.mqtt_bridge: Any = None
        super().__init__(address, EdgeAiRequestHandler)


class EdgeAiRequestHandler(BaseHTTPRequestHandler):
    server: EdgeAiHttpServer
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        try:
            path = urlparse(self.path).path
            if path == "/health":
                self._json(HTTPStatus.OK, {"status": "ok", "timestamp": utc_now_iso()})
                return
            self._authorize()
            if path == "/api/v1/ai/status":
                status_payload = self.server.service.status()
                status_payload["pipeline"] = self.server.pipeline.status()
                status_payload["mqtt"] = (
                    dict(self.server.mqtt_bridge.status())
                    if self.server.mqtt_bridge is not None
                    else {"enabled": False, "started": False}
                )
                self._json(HTTPStatus.OK, status_payload)
                return
            if path.startswith("/api/v1/ai/results/"):
                request_id = unquote(path.removeprefix("/api/v1/ai/results/"))
                if not request_id:
                    raise RequestError(HTTPStatus.BAD_REQUEST, "AI_INVALID_REQUEST", "requestId is required")
                self._json(HTTPStatus.OK, self.server.service.get_result(request_id))
                return
            if path.startswith("/api/v1/ai/feedback/"):
                request_id = unquote(path.removeprefix("/api/v1/ai/feedback/"))
                self._json(
                    HTTPStatus.OK,
                    {"requestId": request_id, "feedback": self.server.service.get_feedback(request_id)},
                )
                return
            if path.startswith("/api/v1/ai/commands/"):
                command_id = unquote(path.removeprefix("/api/v1/ai/commands/"))
                self._json(HTTPStatus.OK, self.server.pipeline.get_command(command_id))
                return
            if path.startswith("/api/v1/ai/frames/"):
                frame_id = unquote(path.removeprefix("/api/v1/ai/frames/"))
                self._frame(frame_id)
                return
            raise RequestError(HTTPStatus.NOT_FOUND, "AI_NOT_FOUND", "endpoint not found")
        except Exception as exc:
            self._handle_exception(exc)

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        self._request_body_consumed = False
        try:
            self._authorize()
            path = urlparse(self.path).path
            if path == "/api/v1/ai/frames":
                image_bytes, metadata, image_content_type = self._read_image_payload()
                frame_metadata = FrameMetadata.from_mapping(metadata)
                accepted = self.server.pipeline.ingest(frame_metadata, image_bytes, image_content_type)
                self._json(HTTPStatus.ACCEPTED, accepted)
                return
            if path == "/api/v1/ai/video-stream":
                result = self.server.service.register_video_stream(self._read_json())
                self._json(HTTPStatus.OK, {"status": "success", "backend": dict(result)})
                return
            raise RequestError(HTTPStatus.NOT_FOUND, "AI_NOT_FOUND", "endpoint not found")
        except Exception as exc:
            self._handle_exception(exc)

    def _authorize(self) -> None:
        expected = self.server.settings.api_token
        if not expected:
            if self.client_address[0] in {"127.0.0.1", "::1"}:
                return
            raise RequestError(HTTPStatus.UNAUTHORIZED, "AI_UNAUTHORIZED", "authentication required")
        supplied = self.headers.get("X-Edge-Token", "")
        authorization = self.headers.get("Authorization", "")
        if authorization.lower().startswith("bearer "):
            supplied = authorization[7:].strip()
        if not supplied or not hmac.compare_digest(supplied, expected):
            raise RequestError(HTTPStatus.UNAUTHORIZED, "AI_UNAUTHORIZED", "invalid edge token")

    def _read_body(self) -> bytes:
        content_length_raw = self.headers.get("Content-Length")
        if content_length_raw is None:
            raise RequestError(HTTPStatus.LENGTH_REQUIRED, "AI_LENGTH_REQUIRED", "Content-Length is required")
        try:
            content_length = int(content_length_raw)
        except ValueError as exc:
            raise RequestError(HTTPStatus.BAD_REQUEST, "AI_INVALID_LENGTH", "invalid Content-Length") from exc
        if content_length < 0:
            raise RequestError(HTTPStatus.BAD_REQUEST, "AI_INVALID_LENGTH", "invalid Content-Length")
        if content_length > self.server.settings.max_request_bytes:
            raise RequestError(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "AI_PAYLOAD_TOO_LARGE", "request body is too large")
        body = self.rfile.read(content_length)
        if len(body) != content_length:
            raise RequestError(HTTPStatus.BAD_REQUEST, "AI_INCOMPLETE_BODY", "incomplete request body")
        self._request_body_consumed = True
        return body

    def _read_json(self) -> Mapping[str, Any]:
        content_type = self.headers.get_content_type()
        if content_type != "application/json":
            raise RequestError(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "AI_UNSUPPORTED_MEDIA", "application/json is required")
        try:
            payload = json.loads(self._read_body().decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RequestError(HTTPStatus.BAD_REQUEST, "AI_INVALID_JSON", "invalid JSON body") from exc
        if not isinstance(payload, dict):
            raise RequestError(HTTPStatus.BAD_REQUEST, "AI_INVALID_JSON", "JSON body must be an object")
        return payload

    def _read_image_payload(self) -> tuple[bytes, Mapping[str, Any], str]:
        content_type = self.headers.get_content_type()
        body = self._read_body()
        if content_type == "application/json":
            try:
                payload = json.loads(body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise RequestError(HTTPStatus.BAD_REQUEST, "AI_INVALID_JSON", "invalid JSON body") from exc
            if not isinstance(payload, dict):
                raise RequestError(HTTPStatus.BAD_REQUEST, "AI_INVALID_JSON", "JSON body must be an object")
            encoded_image = payload.pop("imageBase64", None)
            if not isinstance(encoded_image, str) or not encoded_image:
                raise RequestError(HTTPStatus.BAD_REQUEST, "AI_FILE_REQUIRED", "imageBase64 is required")
            try:
                image_bytes = base64.b64decode(encoded_image, validate=True)
            except (binascii.Error, ValueError) as exc:
                raise RequestError(HTTPStatus.BAD_REQUEST, "AI_INVALID_IMAGE", "imageBase64 is invalid") from exc
            return image_bytes, payload, self._detect_image_type(image_bytes)

        if content_type != "multipart/form-data":
            raise RequestError(
                HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
                "AI_UNSUPPORTED_MEDIA",
                "multipart/form-data or application/json is required",
            )
        raw_message = (
            f"Content-Type: {self.headers.get('Content-Type')}\r\nMIME-Version: 1.0\r\n\r\n".encode("ascii")
            + body
        )
        message = BytesParser(policy=email_policy).parsebytes(raw_message)
        image_bytes: bytes | None = None
        declared_image_type: str | None = None
        metadata: Mapping[str, Any] | None = None
        for part in message.iter_parts():
            name = part.get_param("name", header="content-disposition")
            content = part.get_payload(decode=True) or b""
            if name == "file":
                if part.get_content_type() not in {"image/jpeg", "image/png"}:
                    raise RequestError(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "AI_INVALID_IMAGE", "file must be JPEG or PNG")
                image_bytes = content
                declared_image_type = part.get_content_type()
            elif name == "metadata":
                try:
                    decoded = json.loads(content.decode(part.get_content_charset() or "utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise RequestError(HTTPStatus.BAD_REQUEST, "AI_INVALID_METADATA", "metadata must be valid JSON") from exc
                if not isinstance(decoded, dict):
                    raise RequestError(HTTPStatus.BAD_REQUEST, "AI_INVALID_METADATA", "metadata must be a JSON object")
                metadata = decoded
        if not image_bytes:
            raise RequestError(HTTPStatus.BAD_REQUEST, "AI_FILE_REQUIRED", "multipart file part is required")
        if metadata is None:
            raise RequestError(HTTPStatus.BAD_REQUEST, "AI_METADATA_REQUIRED", "multipart metadata part is required")
        detected_image_type = self._detect_image_type(image_bytes)
        if declared_image_type != detected_image_type:
            raise RequestError(
                HTTPStatus.BAD_REQUEST,
                "AI_INVALID_IMAGE",
                "declared image type does not match file content",
            )
        return image_bytes, metadata, detected_image_type

    def _frame(self, frame_id: str) -> None:
        if not frame_id:
            raise RequestError(HTTPStatus.BAD_REQUEST, "AI_INVALID_REQUEST", "frameId is required")
        metadata, image_bytes, content_type = self.server.pipeline.get_frame(frame_id)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(image_bytes)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Frame-Id", metadata.frame_id)
        self.send_header("X-Source-Drone-Id", metadata.source_drone_id)
        self.send_header("X-Captured-At", metadata.captured_at)
        self.end_headers()
        self.wfile.write(image_bytes)

    @staticmethod
    def _detect_image_type(image_bytes: bytes) -> str:
        if image_bytes.startswith(b"\xff\xd8\xff"):
            return "image/jpeg"
        if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"
        raise RequestError(
            HTTPStatus.BAD_REQUEST,
            "AI_INVALID_IMAGE",
            "image content is not a recognized JPEG or PNG",
        )

    def _handle_exception(self, exc: Exception) -> None:
        # An unread POST body cannot safely share this HTTP/1.1 connection with
        # another request because its bytes remain in the input stream.
        if self.command == "POST" and not getattr(self, "_request_body_consumed", False):
            self.close_connection = True
        if isinstance(exc, RequestError):
            self._error(exc.status, exc.code, exc.message)
        elif isinstance(exc, ValidationError):
            self._error(HTTPStatus.BAD_REQUEST, "AI_INVALID_REQUEST", str(exc))
        elif isinstance(exc, ConflictError):
            self._error(HTTPStatus.CONFLICT, "AI_REQUEST_CONFLICT", str(exc))
        elif isinstance(exc, ResourceNotFoundError):
            self._error(HTTPStatus.NOT_FOUND, "AI_RESULT_NOT_FOUND", str(exc))
        elif isinstance(exc, PublishQueueFullError):
            self._error(HTTPStatus.SERVICE_UNAVAILABLE, "AI_PUBLISH_QUEUE_FULL", str(exc))
        elif isinstance(exc, PipelineBusyError):
            self._error(HTTPStatus.SERVICE_UNAVAILABLE, "AI_PIPELINE_BUSY", str(exc))
        elif isinstance(exc, InferenceError):
            self._error(HTTPStatus.SERVICE_UNAVAILABLE, "AI_INFERENCE_FAILED", str(exc))
        elif isinstance(exc, ValueError):
            self._error(HTTPStatus.BAD_REQUEST, "AI_INVALID_REQUEST", str(exc))
        else:
            LOGGER.exception("Unhandled edge AI server error")
            self._error(HTTPStatus.INTERNAL_SERVER_ERROR, "AI_INTERNAL_ERROR", "internal server error")

    def _error(self, status: HTTPStatus, code: str, message: str) -> None:
        self._json(
            status,
            {
                "status": "error",
                "errorCode": code,
                "message": message,
                "timestamp": utc_now_iso(),
                "details": {"source": "jetson-edge-ai"},
            },
        )

    def _json(self, status: HTTPStatus, payload: Mapping[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(int(status))
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if self.close_connection:
            self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format_string: str, *args: Any) -> None:
        LOGGER.info("%s - %s", self.address_string(), format_string % args)


def create_server(
    settings: Settings,
    service: EdgeAiService | None = None,
    pipeline: ContinuousInferencePipeline | None = None,
    port: int | None = None,
) -> EdgeAiHttpServer:
    if service is None:
        backend_client = None
        if settings.backend_publish_enabled and settings.backend_base_url:
            backend_client = CentralBackendClient(
                base_url=settings.backend_base_url,
                token=settings.backend_token,
                timeout_seconds=settings.backend_timeout_seconds,
                attempts=settings.backend_publish_attempts,
            )
        service = EdgeAiService(settings, build_engine(settings), backend_client)
    if pipeline is None:
        pipeline = ContinuousInferencePipeline(settings, service)
    return EdgeAiHttpServer(
        (settings.host, settings.port if port is None else port),
        settings,
        service,
        pipeline,
    )
