from __future__ import annotations

from email.parser import BytesParser
from email.policy import default as email_policy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
import unittest

from edge_ai_server.backend_client import CentralBackendClient
from edge_ai_server.models import BoundingBox, Detection, InferenceRequest


class CaptureHandler(BaseHTTPRequestHandler):
    records: list[dict[str, object]] = []

    def do_POST(self) -> None:  # noqa: N802
        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)
        self.records.append(
            {
                "path": self.path,
                "headers": dict(self.headers),
                "body": body,
            }
        )
        if self.path == "/api/detections/snapshot":
            response = {"status": "success", "detectionId": "det-test", "imageUrl": "/test.jpg"}
            status = 201
        else:
            response = {"status": "success", "streamId": 12}
            status = 201
        encoded = json.dumps(response).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format_string: str, *args: object) -> None:
        return


class BackendContractTests(unittest.TestCase):
    def setUp(self) -> None:
        CaptureHandler.records = []
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), CaptureHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        host, port = self.server.server_address
        self.client = CentralBackendClient(f"http://{host}:{port}", timeout_seconds=1, attempts=1)

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def test_detection_upload_matches_spring_multipart_contract(self) -> None:
        request = InferenceRequest(
            request_id="req-1",
            mission_id="M-01",
            device_id="V-01",
            captured_at="2026-07-23T09:30:00.000",
            latitude=37.5,
            longitude=127.0,
            altitude=12.0,
            auto_publish=True,
        )
        detection = Detection("smoke", 0.87, BoundingBox(10, 20, 30, 40), "smoke")

        responses = self.client.publish_detections(request, [detection], b"jpeg-bytes", "model-v1")

        self.assertEqual(1, len(responses))
        self.assertEqual(201, responses[0].status_code)
        record = CaptureHandler.records[0]
        self.assertEqual("/api/detections/snapshot", record["path"])
        headers = record["headers"]
        self.assertEqual("req-1:0", headers["X-Idempotency-Key"])

        raw_message = (
            f"Content-Type: {headers['Content-Type']}\r\nMIME-Version: 1.0\r\n\r\n".encode("ascii")
            + record["body"]
        )
        message = BytesParser(policy=email_policy).parsebytes(raw_message)
        parts = {
            part.get_param("name", header="content-disposition"): part.get_payload(decode=True)
            for part in message.iter_parts()
        }
        metadata = json.loads(parts["metadata"].decode("utf-8"))
        self.assertEqual("V-01", metadata["deviceId"])
        self.assertEqual("vehicle", metadata["deviceType"])
        self.assertEqual("smoke", metadata["detectionType"])
        self.assertEqual({"x": 10, "y": 20, "w": 30, "h": 40}, metadata["boundingBox"])
        self.assertEqual("edge_ai_orin", metadata["source"])
        self.assertEqual(b"jpeg-bytes", parts["file"])

    def test_video_stream_registration_matches_backend_contract(self) -> None:
        response = self.client.register_video_stream(
            device_id="V-01",
            stream_url="http://jetson:5000/video",
            status="streaming",
            mission_id="M-01",
        )
        self.assertEqual("success", response["status"])
        record = CaptureHandler.records[0]
        self.assertEqual("/api/video-streams", record["path"])
        payload = json.loads(record["body"].decode("utf-8"))
        self.assertEqual(
            {
                "deviceId": "V-01",
                "deviceType": "vehicle",
                "streamUrl": "http://jetson:5000/video",
                "status": "streaming",
                "missionId": "M-01",
            },
            payload,
        )


if __name__ == "__main__":
    unittest.main()

