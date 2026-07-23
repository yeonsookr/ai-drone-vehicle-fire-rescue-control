"""Continuous drone-frame inference and backend command coordination."""

from __future__ import annotations

from collections import OrderedDict
import copy
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import queue
import threading
import time
from typing import Any, Mapping, Protocol

from .config import Settings
from .models import BackendCommand, BoundingBox, Detection, FrameMetadata, InferenceRequest, utc_now_iso
from .service import ConflictError, EdgeAiService, ResourceNotFoundError


TERMINAL_COMMAND_STATES = {"SUCCEEDED", "FAILED", "EXPIRED"}


class PipelineBusyError(RuntimeError):
    """A bounded pipeline resource cannot accept additional work."""


class PipelineEventSink(Protocol):
    def on_command_update(self, command: Mapping[str, Any]) -> None: ...

    def on_ai_event(self, event: Mapping[str, Any]) -> None: ...


@dataclass(frozen=True, slots=True)
class FramePacket:
    metadata: FrameMetadata
    image_bytes: bytes
    image_content_type: str
    request_id: str
    command_ids: tuple[str, ...] = ()


@dataclass(slots=True)
class EventWindow:
    remaining: int = 0
    deadline: float = 0.0
    cooldown_until: float = 0.0


def _parse_command_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


class ContinuousInferencePipeline:
    """Consumes latest drone frames, performs edge inference and emits evidence."""

    def __init__(self, settings: Settings, service: EdgeAiService) -> None:
        self._settings = settings
        self._service = service
        self._queue: queue.Queue[FramePacket] = queue.Queue(maxsize=settings.frame_queue_size)
        self._buffer: OrderedDict[str, FramePacket] = OrderedDict()
        self._frame_hashes: dict[str, str] = {}
        self._commands: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self._command_fingerprints: dict[str, str] = {}
        self._event_windows: dict[str, EventWindow] = {}
        self._event_sink: PipelineEventSink | None = None
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._frames_received = 0
        self._frames_processed = 0
        self._frames_dropped = 0
        self._worker = threading.Thread(target=self._run, name="edge-ai-frame-worker", daemon=True)
        self._worker.start()

    def set_event_sink(self, event_sink: PipelineEventSink | None) -> None:
        with self._lock:
            self._event_sink = event_sink

    def ingest(
        self,
        metadata: FrameMetadata,
        image_bytes: bytes,
        image_content_type: str,
    ) -> dict[str, Any]:
        fingerprint = hashlib.sha256(image_bytes).hexdigest()
        with self._lock:
            previous = self._frame_hashes.get(metadata.frame_id)
            if previous is not None:
                if previous != fingerprint:
                    raise ConflictError("frameId was already used for different image content")
                return {
                    "status": "duplicate",
                    "frameId": metadata.frame_id,
                    "queued": False,
                }

            self._expire_commands_locked()
            command_ids = self._claim_capture_commands_locked(metadata.frame_id)
            packet = FramePacket(
                metadata=metadata,
                image_bytes=image_bytes,
                image_content_type=image_content_type,
                request_id=metadata.frame_id,
                command_ids=command_ids,
            )
            self._buffer[metadata.frame_id] = packet
            self._frame_hashes[metadata.frame_id] = fingerprint
            self._buffer.move_to_end(metadata.frame_id)
            self._trim_buffer_locked()
            self._frames_received += 1
            for command_id in command_ids:
                self._notify_command_locked(self._commands[command_id])

        dropped = self._enqueue_latest(packet)
        return {
            "status": "accepted",
            "frameId": metadata.frame_id,
            "queued": True,
            "claimedByCommands": list(command_ids),
            "droppedFrameId": dropped.metadata.frame_id if dropped else None,
        }

    def _enqueue_latest(self, packet: FramePacket) -> FramePacket | None:
        dropped: FramePacket | None = None
        try:
            self._queue.put_nowait(packet)
            return None
        except queue.Full:
            try:
                dropped = self._queue.get_nowait()
                self._queue.task_done()
            except queue.Empty:
                pass
        if dropped is not None:
            with self._lock:
                self._frames_dropped += 1
                self._fail_commands_for_dropped_frame_locked(dropped)
        self._queue.put_nowait(packet)
        return dropped

    def submit_command(self, command: BackendCommand) -> dict[str, Any]:
        if command.target_id != self._settings.vehicle_id:
            raise ValueError(
                f"command targetId {command.target_id!r} does not match this Jetson vehicle "
                f"{self._settings.vehicle_id!r}"
            )
        if _parse_command_time(command.expires_at) <= datetime.now(timezone.utc):
            raise ValueError("command is already expired")
        frame_count = command.requested_frame_count()
        fingerprint = command.fingerprint()
        with self._lock:
            previous = self._command_fingerprints.get(command.command_id)
            if previous is not None:
                if previous != fingerprint:
                    raise ConflictError("commandId was already used for a different command")
                duplicate = copy.deepcopy(self._commands[command.command_id])
                duplicate["duplicate"] = True
                return duplicate
            self._make_command_capacity_locked()
            record: dict[str, Any] = {
                "commandId": command.command_id,
                "type": command.command_type,
                "targetId": command.target_id,
                "status": "ACK",
                "issuedAt": command.issued_at,
                "expiresAt": command.expires_at,
                "parameters": dict(command.parameters),
                "expectedFrames": frame_count,
                "remainingCaptureFrames": frame_count,
                "capturedFrameIds": [],
                "frameResults": [],
                "createdAt": utc_now_iso(),
                "updatedAt": utc_now_iso(),
                "duplicate": False,
                "hardwareCommandIssued": False,
            }
            self._commands[command.command_id] = record
            self._command_fingerprints[command.command_id] = fingerprint

            if command.command_type == "reanalyze":
                frame_id_raw = command.parameters.get("frameId")
                frame_id = str(frame_id_raw).strip() if frame_id_raw else self._latest_frame_id_locked()
                if not frame_id or frame_id not in self._buffer:
                    record["status"] = "FAILED"
                    record["errorReason"] = "requested frame is not available in the Jetson buffer"
                    record["remainingCaptureFrames"] = 0
                else:
                    source = self._buffer[frame_id]
                    record["status"] = "RUNNING"
                    record["remainingCaptureFrames"] = 0
                    record["capturedFrameIds"].append(frame_id)
                    reanalysis = FramePacket(
                        metadata=source.metadata,
                        image_bytes=source.image_bytes,
                        image_content_type=source.image_content_type,
                        request_id=f"{command.command_id}:{frame_id}",
                        command_ids=(command.command_id,),
                    )
                    self._enqueue_latest(reanalysis)
            self._notify_command_locked(record)
            return copy.deepcopy(record)

    def _claim_capture_commands_locked(self, frame_id: str) -> tuple[str, ...]:
        claimed: list[str] = []
        for command_id, record in self._commands.items():
            if record["status"] in TERMINAL_COMMAND_STATES:
                continue
            if record["type"] not in {"capture", "burst_capture"}:
                continue
            remaining = int(record["remainingCaptureFrames"])
            if remaining <= 0:
                continue
            record["status"] = "RUNNING"
            record["remainingCaptureFrames"] = remaining - 1
            record["capturedFrameIds"].append(frame_id)
            record["updatedAt"] = utc_now_iso()
            claimed.append(command_id)
        return tuple(claimed)

    def get_command(self, command_id: str) -> dict[str, Any]:
        with self._lock:
            self._expire_commands_locked()
            record = self._commands.get(command_id)
            if record is None:
                raise ResourceNotFoundError(f"command not found: {command_id}")
            return copy.deepcopy(record)

    def get_frame(self, frame_id: str) -> tuple[FrameMetadata, bytes, str]:
        with self._lock:
            packet = self._buffer.get(frame_id)
            if packet is None:
                raise ResourceNotFoundError(f"frame not found: {frame_id}")
            return packet.metadata, packet.image_bytes, packet.image_content_type

    def _run(self) -> None:
        while not self._stop.is_set() or not self._queue.empty():
            try:
                packet = self._queue.get(timeout=0.1)
            except queue.Empty:
                continue
            try:
                self._process(packet)
            finally:
                self._queue.task_done()

    def _process(self, packet: FramePacket) -> None:
        request = packet.metadata.to_inference_request(
            self._settings.vehicle_id,
            request_id=packet.request_id,
        )
        try:
            result = self._service.infer(
                request,
                packet.image_bytes,
                packet.image_content_type,
            )
            detections = self._detections_from_result(result)
            proactive_types = self._select_proactive_types(detections)
            publish_reasons: list[str] = []
            if proactive_types:
                publish_reasons.append("proactive:" + ",".join(sorted(proactive_types)))
            if packet.command_ids:
                publish_reasons.append("command:" + ",".join(packet.command_ids))
            if detections and publish_reasons:
                self._notify_ai_event(packet, request, detections, publish_reasons)
                self._service.publish_evidence(
                    request,
                    detections,
                    packet.image_bytes,
                    packet.image_content_type,
                    reason=";".join(publish_reasons),
                )
            current_result = self._service.get_result(request.request_id)
            with self._lock:
                self._frames_processed += 1
                self._complete_commands_locked(
                    packet,
                    result,
                    str(current_result.get("publishState", "not_required")),
                )
        except Exception as exc:
            with self._lock:
                self._frames_processed += 1
                for command_id in packet.command_ids:
                    record = self._commands.get(command_id)
                    if record is not None and record["status"] not in TERMINAL_COMMAND_STATES:
                        record["status"] = "FAILED"
                        record["errorReason"] = str(exc)
                        record["updatedAt"] = utc_now_iso()
                        self._notify_command_locked(record)

    @staticmethod
    def _detections_from_result(result: dict[str, Any]) -> list[Detection]:
        detections: list[Detection] = []
        for item in result.get("detections", []):
            box = item["boundingBox"]
            detections.append(
                Detection(
                    detection_type=item["detectionType"],
                    confidence=float(item["confidence"]),
                    bounding_box=BoundingBox(
                        x=int(box["x"]),
                        y=int(box["y"]),
                        width=int(box["w"]),
                        height=int(box["h"]),
                    ),
                    source_label=str(item.get("sourceLabel", "")),
                )
            )
        return detections

    def _select_proactive_types(self, detections: list[Detection]) -> set[str]:
        now = time.monotonic()
        selected: set[str] = set()
        with self._lock:
            for detection_type in {item.detection_type for item in detections}:
                window = self._event_windows.setdefault(detection_type, EventWindow())
                if window.remaining > 0 and now > window.deadline:
                    window.remaining = 0
                    window.cooldown_until = window.deadline + self._settings.event_cooldown_seconds
                if window.remaining == 0 and now >= window.cooldown_until:
                    window.remaining = self._settings.evidence_frame_count
                    window.deadline = now + self._settings.evidence_window_seconds
                if window.remaining > 0 and now <= window.deadline:
                    selected.add(detection_type)
                    window.remaining -= 1
                    if window.remaining == 0:
                        window.cooldown_until = now + self._settings.event_cooldown_seconds
        return selected

    def _complete_commands_locked(
        self,
        packet: FramePacket,
        result: dict[str, Any],
        publish_state: str,
    ) -> None:
        for command_id in packet.command_ids:
            record = self._commands.get(command_id)
            if record is None or record["status"] in TERMINAL_COMMAND_STATES:
                continue
            record["frameResults"].append(
                {
                    "frameId": packet.metadata.frame_id,
                    "requestId": packet.request_id,
                    "detectionCount": result["detectionCount"],
                    "resultUrl": f"/api/v1/ai/results/{packet.request_id}",
                    "frameUrl": f"/api/v1/ai/frames/{packet.metadata.frame_id}",
                    "publishState": publish_state,
                }
            )
            if len(record["frameResults"]) >= int(record["expectedFrames"]):
                record["status"] = "SUCCEEDED"
                record["completedAt"] = utc_now_iso()
            record["updatedAt"] = utc_now_iso()
            self._notify_command_locked(record)

    def _expire_commands_locked(self) -> None:
        now = datetime.now(timezone.utc)
        for record in self._commands.values():
            if record["status"] in TERMINAL_COMMAND_STATES:
                continue
            # Once all requested frames are captured, allow queued inference to finish.
            if int(record["remainingCaptureFrames"]) == 0:
                continue
            if _parse_command_time(record["expiresAt"]) <= now:
                record["status"] = "EXPIRED"
                record["errorReason"] = "command expired before all requested frames arrived"
                record["updatedAt"] = utc_now_iso()
                self._notify_command_locked(record)

    def _fail_commands_for_dropped_frame_locked(self, packet: FramePacket) -> None:
        for command_id in packet.command_ids:
            record = self._commands.get(command_id)
            if record is not None and record["status"] not in TERMINAL_COMMAND_STATES:
                record["status"] = "FAILED"
                record["errorReason"] = "captured frame was dropped because the inference queue was full"
                record["updatedAt"] = utc_now_iso()
                self._notify_command_locked(record)

    def _notify_command_locked(self, record: Mapping[str, Any]) -> None:
        if self._event_sink is not None:
            self._event_sink.on_command_update(copy.deepcopy(record))

    def _notify_ai_event(
        self,
        packet: FramePacket,
        request: InferenceRequest,
        detections: list[Detection],
        publish_reasons: list[str],
    ) -> None:
        with self._lock:
            sink = self._event_sink
        if sink is None:
            return
        sink.on_ai_event(
            {
                "schemaVersion": "1.0",
                "eventId": f"edge-{packet.metadata.frame_id}",
                "frameId": packet.metadata.frame_id,
                "missionId": request.mission_id,
                "vehicleId": self._settings.vehicle_id,
                "droneId": packet.metadata.source_drone_id,
                "detectedAt": request.captured_at,
                "location": {
                    "latitude": request.latitude,
                    "longitude": request.longitude,
                    "altitude": request.altitude,
                },
                "modelVersion": self._service.status()["engine"]["modelVersion"],
                "detections": [item.to_dict(self._settings.review_threshold) for item in detections],
                "reason": ";".join(publish_reasons),
                "snapshotTransport": "http",
                "snapshotUploadState": "queued",
                "timestamp": utc_now_iso(),
            }
        )

    def _trim_buffer_locked(self) -> None:
        while len(self._buffer) > self._settings.frame_buffer_size:
            frame_id, _ = self._buffer.popitem(last=False)
            self._frame_hashes.pop(frame_id, None)

    def _latest_frame_id_locked(self) -> str | None:
        return next(reversed(self._buffer), None) if self._buffer else None

    def _make_command_capacity_locked(self) -> None:
        while len(self._commands) >= self._settings.command_cache_size:
            removable = next(
                (command_id for command_id, item in self._commands.items() if item["status"] in TERMINAL_COMMAND_STATES),
                None,
            )
            if removable is None:
                raise PipelineBusyError("command cache is full of active commands")
            self._commands.pop(removable, None)
            self._command_fingerprints.pop(removable, None)

    def status(self) -> dict[str, Any]:
        with self._lock:
            self._expire_commands_locked()
            command_counts: dict[str, int] = {}
            for record in self._commands.values():
                state = str(record["status"])
                command_counts[state] = command_counts.get(state, 0) + 1
            return {
                "mode": "continuous_drone_frames",
                "framesReceived": self._frames_received,
                "framesProcessed": self._frames_processed,
                "framesDropped": self._frames_dropped,
                "queuedFrames": self._queue.qsize(),
                "bufferedFrames": len(self._buffer),
                "evidenceFrameCount": self._settings.evidence_frame_count,
                "eventCooldownSeconds": self._settings.event_cooldown_seconds,
                "commands": command_counts,
            }

    def wait_until_idle(self, timeout: float = 5.0) -> bool:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self._queue.unfinished_tasks == 0:
                return True
            time.sleep(0.01)
        return self._queue.unfinished_tasks == 0

    def shutdown(self, timeout: float = 5.0) -> None:
        self._stop.set()
        self._worker.join(timeout=timeout)
