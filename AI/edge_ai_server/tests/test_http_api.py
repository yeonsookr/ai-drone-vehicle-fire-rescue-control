from __future__ import annotations

from http.client import HTTPConnection
import json
import threading
import unittest

from edge_ai_server.api_server import create_server
from edge_ai_server.backend_client import encode_multipart
from edge_ai_server.config import Settings
from edge_ai_server.engine import MockInferenceEngine
from edge_ai_server.models import BoundingBox, Detection
from edge_ai_server.pipeline import ContinuousInferencePipeline
from edge_ai_server.service import EdgeAiService


class EdgeAiHttpApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.settings = Settings(
            host="127.0.0.1",
            port=5001,
            api_token="test-token",
            backend_publish_enabled=False,
            model_version="mock-contract-v1",
            evidence_frame_count=2,
            event_cooldown_seconds=60,
        )
        engine = MockInferenceEngine(
            detections=[Detection("forest_fire", 0.91, BoundingBox(1, 2, 30, 40), "fire")],
            model_version="mock-contract-v1",
        )
        self.service = EdgeAiService(self.settings, engine, None)
        self.pipeline = ContinuousInferencePipeline(self.settings, self.service)
        self.server = create_server(self.settings, self.service, self.pipeline, port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.connection = HTTPConnection(*self.server.server_address, timeout=2)

    def tearDown(self) -> None:
        self.connection.close()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.pipeline.shutdown()
        self.service.shutdown()

    def _json_request(
        self,
        method: str,
        path: str,
        payload: dict[str, object] | None = None,
        token: str | None = "test-token",
    ) -> tuple[int, dict[str, object]]:
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {"Accept": "application/json"}
        if payload is not None:
            headers["Content-Type"] = "application/json"
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"
        self.connection.request(method, path, body=body, headers=headers)
        response = self.connection.getresponse()
        parsed = json.loads(response.read().decode("utf-8"))
        return response.status, parsed

    @staticmethod
    def _frame_metadata(frame_id: str) -> dict[str, object]:
        return {
            "frameId": frame_id,
            "missionId": "M-01",
            "sourceDroneId": "D-01",
            "capturedAt": "2026-07-23T09:30:00",
            "latitude": 37.5,
            "longitude": 127.0,
            "altitude": 12.0,
        }

    def _send_frame(
        self,
        frame_id: str,
        content: bytes = b"\xff\xd8\xffmock-jpeg",
        declared_type: str = "image/jpeg",
    ) -> tuple[int, dict[str, object]]:
        body, content_type = encode_multipart(
            {"metadata": json.dumps(self._frame_metadata(frame_id))},
            [("file", f"{frame_id}.jpg", declared_type, content)],
        )
        self.connection.request(
            "POST",
            "/api/v1/ai/frames",
            body=body,
            headers={
                "Content-Type": content_type,
                "Authorization": "Bearer test-token",
                "Accept": "application/json",
            },
        )
        response = self.connection.getresponse()
        parsed = json.loads(response.read().decode("utf-8"))
        return response.status, parsed

    def test_health_is_public_and_status_reports_continuous_mode(self) -> None:
        status, body = self._json_request("GET", "/health", token=None)
        self.assertEqual(200, status)
        self.assertEqual("ok", body["status"])

        status, body = self._json_request("GET", "/api/v1/ai/status")
        self.assertEqual(200, status)
        self.assertEqual("continuous_drone_frames", body["pipeline"]["mode"])

        status, body = self._json_request("GET", "/api/v1/ai/status", token=None)
        self.assertEqual(401, status)
        self.assertEqual("AI_UNAUTHORIZED", body["errorCode"])

    def test_drone_frame_is_accepted_and_continuously_inferred(self) -> None:
        status, accepted = self._send_frame("frame-1")
        self.assertEqual(202, status)
        self.assertEqual("accepted", accepted["status"])
        self.assertTrue(self.pipeline.wait_until_idle())

        status, result = self._json_request("GET", "/api/v1/ai/results/frame-1")
        self.assertEqual(200, status)
        self.assertEqual(1, result["detectionCount"])
        self.assertEqual("forest_fire", result["detections"][0]["detectionType"])
        self.assertFalse(result["hardwareCommandIssued"])

    def test_backend_commands_are_not_accepted_over_http(self) -> None:
        command = {
            "commandId": "cmd-capture-1",
            "type": "capture",
            "targetId": "V-01",
            "issuedAt": "2026-07-23T09:30:00",
            "expiresAt": "2099-07-23T09:31:00Z",
            "parameters": {},
        }
        status, body = self._json_request("POST", "/api/v1/ai/commands", command)
        self.assertEqual(404, status)
        self.assertEqual("AI_NOT_FOUND", body["errorCode"])

        feedback = {
            "requestId": "feedback-1",
            "frameId": "frame-1",
            "decision": "confirmed",
        }
        status, body = self._json_request("POST", "/api/v1/ai/feedback", feedback)
        self.assertEqual(404, status)
        self.assertEqual("AI_NOT_FOUND", body["errorCode"])

    def test_buffered_frame_can_be_downloaded_by_backend(self) -> None:
        content = b"\x89PNG\r\n\x1a\nmock-png"
        status, _ = self._send_frame("frame-png", content, "image/png")
        self.assertEqual(202, status)
        self.connection.request(
            "GET",
            "/api/v1/ai/frames/frame-png",
            headers={"Authorization": "Bearer test-token"},
        )
        response = self.connection.getresponse()
        body = response.read()
        self.assertEqual(200, response.status)
        self.assertEqual("image/png", response.getheader("Content-Type"))
        self.assertEqual("D-01", response.getheader("X-Source-Drone-Id"))
        self.assertEqual(content, body)

    def test_duplicate_and_mislabeled_frames_are_rejected_safely(self) -> None:
        status, _ = self._send_frame("frame-duplicate")
        self.assertEqual(202, status)
        status, duplicate = self._send_frame("frame-duplicate")
        self.assertEqual(202, status)
        self.assertEqual("duplicate", duplicate["status"])

        status, error = self._send_frame(
            "frame-mislabeled",
            b"\x89PNG\r\n\x1a\nmock-png",
            "image/jpeg",
        )
        self.assertEqual(400, status)
        self.assertEqual("AI_INVALID_IMAGE", error["errorCode"])


if __name__ == "__main__":
    unittest.main()
