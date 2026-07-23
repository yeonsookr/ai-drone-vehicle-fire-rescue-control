"""Application service coordinating inference, deduplication and publishing."""

from __future__ import annotations

from collections import OrderedDict
from concurrent.futures import Future, ThreadPoolExecutor, wait
import copy
import hashlib
import threading
import time
from typing import Any, Mapping

from .backend_client import CentralBackendClient, PublishResponse
from .config import Settings
from .engine import InferenceEngine
from .models import Detection, InferenceRequest, OperatorFeedback, utc_now_iso


class ConflictError(RuntimeError):
    """A request ID was reused for a different payload or is still running."""


class ResourceNotFoundError(LookupError):
    """Requested result does not exist in the bounded local cache."""


class PublishQueueFullError(RuntimeError):
    """The bounded backend publishing queue cannot accept more work."""


class EdgeAiService:
    def __init__(
        self,
        settings: Settings,
        engine: InferenceEngine,
        backend_client: CentralBackendClient | None,
    ) -> None:
        self._settings = settings
        self._engine = engine
        self._backend_client = backend_client
        self._results: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self._fingerprints: dict[str, str] = {}
        self._inflight: set[str] = set()
        self._feedback: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
        self._lock = threading.RLock()
        self._started_at = time.monotonic()
        self._request_count = 0
        self._failure_count = 0
        self._publish_slots = threading.BoundedSemaphore(settings.publish_queue_size)
        self._publisher = ThreadPoolExecutor(max_workers=1, thread_name_prefix="edge-ai-publisher")
        self._publish_futures: set[Future[list[PublishResponse]]] = set()

    def infer(
        self,
        request: InferenceRequest,
        image_bytes: bytes,
        image_content_type: str = "image/jpeg",
    ) -> dict[str, Any]:
        fingerprint = hashlib.sha256(image_bytes).hexdigest()
        with self._lock:
            previous_fingerprint = self._fingerprints.get(request.request_id)
            if previous_fingerprint is not None:
                if previous_fingerprint != fingerprint:
                    raise ConflictError("requestId was already used for a different image")
                if request.request_id in self._results:
                    duplicate = copy.deepcopy(self._results[request.request_id])
                    duplicate["duplicate"] = True
                    return duplicate
                raise ConflictError("requestId is already being processed")
            self._fingerprints[request.request_id] = fingerprint
            self._inflight.add(request.request_id)
            self._request_count += 1

        started_wall = utc_now_iso()
        started = time.perf_counter()
        try:
            detections = self._engine.infer(image_bytes)
        except Exception:
            with self._lock:
                self._failure_count += 1
                self._inflight.discard(request.request_id)
                self._fingerprints.pop(request.request_id, None)
            raise

        elapsed_ms = round((time.perf_counter() - started) * 1000.0, 3)
        if not detections:
            publish_state = "not_required"
        elif not request.auto_publish:
            publish_state = "skipped"
        elif not self._publishing_enabled:
            publish_state = "disabled"
        else:
            publish_state = "queued"

        result: dict[str, Any] = {
            "status": "success",
            "requestId": request.request_id,
            "missionId": request.mission_id,
            "deviceId": request.device_id,
            "sourceDroneId": request.source_drone_id,
            "modelVersion": self._engine.model_version,
            "startedAt": started_wall,
            "completedAt": utc_now_iso(),
            "inferenceMs": elapsed_ms,
            "detectionCount": len(detections),
            "detections": [item.to_dict(self._settings.review_threshold) for item in detections],
            "publishState": publish_state,
            "duplicate": False,
            "hardwareCommandIssued": False,
        }
        with self._lock:
            self._inflight.discard(request.request_id)
            self._store_result(request.request_id, result)

        if publish_state == "queued":
            self._submit_publish(request, detections, image_bytes, image_content_type)
        return copy.deepcopy(result)

    @property
    def _publishing_enabled(self) -> bool:
        return (
            self._settings.backend_publish_enabled
            and self._backend_client is not None
            and self._backend_client.enabled
        )

    def _submit_publish(
        self,
        request: InferenceRequest,
        detections: list[Any],
        image_bytes: bytes,
        image_content_type: str,
    ) -> None:
        if not self._publish_slots.acquire(blocking=False):
            self._update_publish_state(request.request_id, "queue_full", "backend publish queue is full")
            raise PublishQueueFullError("backend publish queue is full")

        assert self._backend_client is not None
        future = self._publisher.submit(
            self._backend_client.publish_detections,
            request,
            detections,
            image_bytes,
            self._engine.model_version,
            image_content_type,
        )
        with self._lock:
            self._publish_futures.add(future)

        def on_complete(completed: Future[list[PublishResponse]]) -> None:
            try:
                responses = completed.result()
                response_payload = [
                    {
                        "detectionIndex": item.detection_index,
                        "statusCode": item.status_code,
                        "body": dict(item.body),
                    }
                    for item in responses
                ]
                self._update_publish_state(request.request_id, "delivered", responses=response_payload)
            except Exception as exc:
                self._update_publish_state(request.request_id, "failed", str(exc))
            finally:
                with self._lock:
                    self._publish_futures.discard(completed)
                self._publish_slots.release()

        future.add_done_callback(on_complete)

    def publish_evidence(
        self,
        request: InferenceRequest,
        detections: list[Detection],
        image_bytes: bytes,
        image_content_type: str,
        reason: str,
    ) -> None:
        """Publish a frame selected by proactive detection or a backend command."""
        if not detections:
            return
        if not self._publishing_enabled:
            self._update_publish_state(request.request_id, "disabled")
            return
        with self._lock:
            result = self._results.get(request.request_id)
            if result is None:
                raise ResourceNotFoundError(f"result not found: {request.request_id}")
            result["publishState"] = "queued"
            result["publishReason"] = reason
        self._submit_publish(request, detections, image_bytes, image_content_type)

    def _update_publish_state(
        self,
        request_id: str,
        state: str,
        error: str | None = None,
        responses: list[dict[str, Any]] | None = None,
    ) -> None:
        with self._lock:
            result = self._results.get(request_id)
            if result is None:
                return
            result["publishState"] = state
            result["publishUpdatedAt"] = utc_now_iso()
            if error is not None:
                result["publishError"] = error
            if responses is not None:
                result["backendResponses"] = responses

    def _store_result(self, request_id: str, result: dict[str, Any]) -> None:
        self._results[request_id] = result
        self._results.move_to_end(request_id)
        while len(self._results) > self._settings.result_cache_size:
            evicted_request_id, _ = self._results.popitem(last=False)
            self._fingerprints.pop(evicted_request_id, None)
            self._feedback.pop(evicted_request_id, None)

    def get_result(self, request_id: str) -> dict[str, Any]:
        with self._lock:
            result = self._results.get(request_id)
            if result is None:
                raise ResourceNotFoundError(f"result not found: {request_id}")
            return copy.deepcopy(result)

    def record_feedback(self, feedback: OperatorFeedback) -> dict[str, Any]:
        with self._lock:
            if feedback.request_id not in self._results:
                raise ResourceNotFoundError(f"result not found: {feedback.request_id}")
            entries = self._feedback.setdefault(feedback.request_id, [])
            payload = feedback.to_dict()
            entries.append(payload)
            self._feedback.move_to_end(feedback.request_id)
            self._results[feedback.request_id]["latestOperatorFeedback"] = payload
            return copy.deepcopy(payload)

    def get_feedback(self, request_id: str) -> list[dict[str, Any]]:
        with self._lock:
            if request_id not in self._results:
                raise ResourceNotFoundError(f"result not found: {request_id}")
            return copy.deepcopy(self._feedback.get(request_id, []))

    def register_video_stream(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        if self._backend_client is None or not self._backend_client.enabled:
            raise RuntimeError("backend client is disabled")
        stream_url = payload.get("streamUrl")
        status = payload.get("status")
        if not isinstance(stream_url, str) or not stream_url.strip():
            raise ValueError("streamUrl is required")
        if status not in {"streaming", "inactive", "error"}:
            raise ValueError("status must be streaming, inactive, or error")
        mission_id = payload.get("missionId")
        return self._backend_client.register_video_stream(
            device_id=self._settings.vehicle_id,
            stream_url=stream_url.strip(),
            status=str(status),
            mission_id=str(mission_id).strip() if mission_id else None,
        )

    def status(self) -> dict[str, Any]:
        with self._lock:
            pending_publishes = len(self._publish_futures)
            cached_results = len(self._results)
            inflight = len(self._inflight)
            requests = self._request_count
            failures = self._failure_count
        return {
            "status": "ready",
            "vehicleId": self._settings.vehicle_id,
            "uptimeSeconds": round(time.monotonic() - self._started_at, 3),
            "requests": requests,
            "failures": failures,
            "inflight": inflight,
            "cachedResults": cached_results,
            "pendingPublishes": pending_publishes,
            "backendPublishing": self._publishing_enabled,
            "engine": dict(self._engine.status()),
        }

    def wait_for_publishing(self, timeout: float = 5.0) -> None:
        with self._lock:
            futures = list(self._publish_futures)
        if futures:
            wait(futures, timeout=timeout)

    def shutdown(self, wait_for_jobs: bool = True) -> None:
        self._publisher.shutdown(wait=wait_for_jobs, cancel_futures=not wait_for_jobs)
