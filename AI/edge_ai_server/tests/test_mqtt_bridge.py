from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import threading
import unittest

from edge_ai_server.config import Settings
from edge_ai_server.engine import MockInferenceEngine
from edge_ai_server.models import BoundingBox, Detection, FrameMetadata
from edge_ai_server.mqtt_bridge import EdgeMqttBridge
from edge_ai_server.pipeline import ContinuousInferencePipeline
from edge_ai_server.service import EdgeAiService


class FakeMqttTransport:
    def __init__(self) -> None:
        self.subscriptions: list[tuple[str, int]] = []
        self.messages: list[dict[str, object]] = []
        self.callback = None
        self.started = False
        self._lock = threading.Lock()

    def start(self, subscriptions: list[tuple[str, int]], callback: object) -> None:
        self.subscriptions = list(subscriptions)
        self.callback = callback
        self.started = True

    def publish(self, topic: str, payload: bytes, qos: int, retain: bool = False) -> None:
        with self._lock:
            self.messages.append(
                {
                    "topic": topic,
                    "payload": json.loads(payload.decode("utf-8")),
                    "qos": qos,
                    "retain": retain,
                }
            )

    def deliver(self, topic: str, payload: dict[str, object]) -> None:
        assert self.callback is not None
        self.callback(topic, json.dumps(payload).encode("utf-8"))

    def stop(self) -> None:
        self.started = False

    def status(self) -> dict[str, object]:
        return {"transport": "fake", "connected": self.started}

    def payloads_for(self, topic: str) -> list[dict[str, object]]:
        with self._lock:
            return [item["payload"] for item in self.messages if item["topic"] == topic]


class MqttBridgeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.settings = Settings(
            host="127.0.0.1",
            backend_publish_enabled=False,
            mqtt_enabled=True,
            mqtt_status_interval_seconds=60,
            evidence_frame_count=1,
            event_cooldown_seconds=60,
        )
        engine = MockInferenceEngine(
            detections=[Detection("smoke", 0.88, BoundingBox(10, 20, 30, 40), "smoke")],
            model_version="mqtt-contract-v1",
        )
        self.service = EdgeAiService(self.settings, engine, None)
        self.pipeline = ContinuousInferencePipeline(self.settings, self.service)
        self.transport = FakeMqttTransport()
        self.bridge = EdgeMqttBridge(
            self.settings,
            self.service,
            self.pipeline,
            self.transport,
        )
        self.bridge.start()

    def tearDown(self) -> None:
        self.bridge.stop()
        self.pipeline.shutdown()
        self.service.shutdown()

    @staticmethod
    def _frame(frame_id: str) -> FrameMetadata:
        return FrameMetadata(
            frame_id=frame_id,
            mission_id="M-01",
            source_drone_id="D-01",
            captured_at="2026-07-23T09:30:00.000",
            latitude=37.5,
            longitude=127.0,
            altitude=15.0,
        )

    def test_subscriptions_and_retained_online_status(self) -> None:
        self.assertEqual(
            [
                ("vehicle/V-01/command", 1),
                ("vehicle/V-01/ai/command", 1),
                ("vehicle/V-01/ai/feedback", 1),
            ],
            self.transport.subscriptions,
        )
        statuses = self.transport.payloads_for("vehicle/V-01/ai/status")
        self.assertEqual("online", statuses[0]["state"])
        status_messages = [item for item in self.transport.messages if item["topic"] == "vehicle/V-01/ai/status"]
        self.assertTrue(status_messages[0]["retain"])

    def test_proactive_detection_publishes_mqtt_metadata_event(self) -> None:
        self.pipeline.ingest(self._frame("mqtt-frame-1"), b"\xff\xd8\xffframe", "image/jpeg")
        self.assertTrue(self.pipeline.wait_until_idle())
        events = self.transport.payloads_for("vehicle/V-01/ai/events")
        self.assertEqual(1, len(events))
        event = events[0]
        self.assertEqual("mqtt-frame-1", event["frameId"])
        self.assertEqual("D-01", event["droneId"])
        self.assertEqual("smoke", event["detections"][0]["detectionType"])
        self.assertEqual("http", event["snapshotTransport"])

    def test_mqtt_capture_command_emits_ack_running_and_success(self) -> None:
        now = datetime.now(timezone.utc)
        self.transport.deliver(
            "vehicle/V-01/ai/command",
            {
                "commandId": "cmd-mqtt-1",
                "type": "capture",
                "targetId": "V-01",
                "issuedAt": now.isoformat(),
                "expiresAt": (now + timedelta(minutes=1)).isoformat(),
                "parameters": {},
            },
        )
        self.pipeline.ingest(self._frame("mqtt-command-frame"), b"\xff\xd8\xffcommand", "image/jpeg")
        self.assertTrue(self.pipeline.wait_until_idle())
        topic = "vehicle/V-01/ai/command/cmd-mqtt-1/status"
        statuses = [item["status"] for item in self.transport.payloads_for(topic)]
        self.assertEqual(["ACK", "RUNNING", "SUCCEEDED"], statuses)

    def test_current_spring_command_topic_and_payload_are_compatible(self) -> None:
        now = datetime.now(timezone.utc)
        self.transport.deliver(
            "vehicle/V-01/command",
            {
                "command_id": "cmd-spring-1",
                "type": "capture",
                "issued_at": now.isoformat(),
                "parameters": {},
            },
        )
        self.pipeline.ingest(self._frame("spring-command-frame"), b"\xff\xd8\xffcommand", "image/jpeg")
        self.assertTrue(self.pipeline.wait_until_idle())
        topic = "vehicle/V-01/ai/command/cmd-spring-1/status"
        statuses = [item["status"] for item in self.transport.payloads_for(topic)]
        self.assertEqual(["ACK", "RUNNING", "SUCCEEDED"], statuses)

    def test_operator_feedback_is_received_over_mqtt(self) -> None:
        self.pipeline.ingest(self._frame("mqtt-feedback-frame"), b"\xff\xd8\xfffeedback", "image/jpeg")
        self.assertTrue(self.pipeline.wait_until_idle())
        self.transport.deliver(
            "vehicle/V-01/ai/feedback",
            {
                "requestId": "mqtt-feedback-frame",
                "eventId": "det-1",
                "judgment": "approved",
                "reason": "operator confirmed",
                "judgedAt": datetime.now(timezone.utc).isoformat(),
            },
        )
        feedback = self.service.get_feedback("mqtt-feedback-frame")
        self.assertEqual("approved", feedback[0]["judgment"])
        acks = self.transport.payloads_for(
            "vehicle/V-01/ai/feedback/mqtt-feedback-frame/status"
        )
        self.assertEqual("ACK", acks[0]["status"])


if __name__ == "__main__":
    unittest.main()
