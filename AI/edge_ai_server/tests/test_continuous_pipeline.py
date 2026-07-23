from __future__ import annotations

from datetime import datetime, timedelta, timezone
import threading
import unittest

from edge_ai_server.backend_client import PublishResponse
from edge_ai_server.config import Settings
from edge_ai_server.engine import MockInferenceEngine
from edge_ai_server.models import BackendCommand, BoundingBox, Detection, FrameMetadata
from edge_ai_server.pipeline import ContinuousInferencePipeline
from edge_ai_server.service import EdgeAiService


class RecordingBackendClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []
        self._lock = threading.Lock()

    @property
    def enabled(self) -> bool:
        return True

    def publish_detections(
        self,
        request: object,
        detections: list[Detection],
        image_bytes: bytes,
        model_version: str,
        image_content_type: str = "image/jpeg",
    ) -> list[PublishResponse]:
        with self._lock:
            self.calls.append(
                {
                    "requestId": request.request_id,
                    "detections": detections,
                    "image": image_bytes,
                    "modelVersion": model_version,
                    "contentType": image_content_type,
                }
            )
        return [PublishResponse(0, 201, {"status": "success"})]


def future_iso(minutes: int = 5) -> str:
    return (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()


def frame(frame_id: str) -> FrameMetadata:
    return FrameMetadata(
        frame_id=frame_id,
        mission_id="M-01",
        source_drone_id="D-01",
        captured_at="2026-07-23T09:30:00.000",
        latitude=37.5,
        longitude=127.0,
        altitude=10.0,
    )


class ContinuousPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.backend = RecordingBackendClient()
        self.settings = Settings(
            host="127.0.0.1",
            backend_publish_enabled=True,
            evidence_frame_count=3,
            evidence_window_seconds=10,
            event_cooldown_seconds=60,
            frame_queue_size=8,
            frame_buffer_size=10,
        )
        engine = MockInferenceEngine(
            detections=[Detection("smoke", 0.8, BoundingBox(1, 2, 3, 4), "smoke")]
        )
        self.service = EdgeAiService(self.settings, engine, self.backend)
        self.pipeline = ContinuousInferencePipeline(self.settings, self.service)

    def tearDown(self) -> None:
        self.pipeline.shutdown()
        self.service.shutdown()

    def test_detection_sends_configured_evidence_frames_then_cools_down(self) -> None:
        for index in range(4):
            self.pipeline.ingest(frame(f"frame-{index}"), b"\xff\xd8\xffimage" + bytes([index]), "image/jpeg")
        self.assertTrue(self.pipeline.wait_until_idle())
        self.service.wait_for_publishing()
        self.assertEqual(3, len(self.backend.calls))
        self.assertEqual(["frame-0", "frame-1", "frame-2"], [item["requestId"] for item in self.backend.calls])

    def test_burst_command_uses_next_two_frames_and_tracks_completion(self) -> None:
        command = BackendCommand.from_mapping(
            {
                "commandId": "cmd-burst",
                "type": "burst_capture",
                "targetId": "V-01",
                "issuedAt": datetime.now(timezone.utc).isoformat(),
                "expiresAt": future_iso(),
                "parameters": {"count": 2},
            }
        )
        accepted = self.pipeline.submit_command(command)
        self.assertEqual("ACK", accepted["status"])
        first = self.pipeline.ingest(frame("burst-1"), b"\xff\xd8\xffone", "image/jpeg")
        second = self.pipeline.ingest(frame("burst-2"), b"\xff\xd8\xfftwo", "image/jpeg")
        self.assertEqual(["cmd-burst"], first["claimedByCommands"])
        self.assertEqual(["cmd-burst"], second["claimedByCommands"])
        self.assertTrue(self.pipeline.wait_until_idle())
        self.service.wait_for_publishing()
        completed = self.pipeline.get_command("cmd-burst")
        self.assertEqual("SUCCEEDED", completed["status"])
        self.assertEqual(2, len(completed["frameResults"]))

    def test_reanalyze_uses_requested_buffered_frame(self) -> None:
        self.pipeline.ingest(frame("saved-frame"), b"\xff\xd8\xffsaved", "image/jpeg")
        self.assertTrue(self.pipeline.wait_until_idle())
        command = BackendCommand.from_mapping(
            {
                "commandId": "cmd-reanalyze",
                "type": "reanalyze",
                "targetId": "V-01",
                "issuedAt": datetime.now(timezone.utc).isoformat(),
                "expiresAt": future_iso(),
                "parameters": {"frameId": "saved-frame"},
            }
        )
        accepted = self.pipeline.submit_command(command)
        self.assertEqual("RUNNING", accepted["status"])
        self.assertTrue(self.pipeline.wait_until_idle())
        completed = self.pipeline.get_command("cmd-reanalyze")
        self.assertEqual("SUCCEEDED", completed["status"])
        self.assertEqual("saved-frame", completed["frameResults"][0]["frameId"])


if __name__ == "__main__":
    unittest.main()

