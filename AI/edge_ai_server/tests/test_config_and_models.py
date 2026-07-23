from __future__ import annotations

import unittest

from edge_ai_server.config import Settings
from edge_ai_server.models import InferenceRequest, OperatorFeedback, ValidationError


class SettingsTests(unittest.TestCase):
    def test_remote_binding_requires_token(self) -> None:
        with self.assertRaisesRegex(ValueError, "API_TOKEN"):
            Settings.from_env(
                {
                    "EDGE_AI_HOST": "0.0.0.0",
                    "EDGE_AI_ENGINE": "mock",
                    "BACKEND_PUBLISH_ENABLED": "false",
                }
            )

    def test_mock_local_settings_need_no_external_dependencies(self) -> None:
        settings = Settings.from_env(
            {
                "EDGE_AI_HOST": "127.0.0.1",
                "EDGE_AI_ENGINE": "mock",
                "BACKEND_PUBLISH_ENABLED": "false",
            }
        )
        self.assertEqual("mock", settings.engine)
        self.assertFalse(settings.backend_publish_enabled)


class DomainModelTests(unittest.TestCase):
    def test_inference_request_accepts_camel_case_contract(self) -> None:
        request = InferenceRequest.from_mapping(
            {
                "requestId": "req-1",
                "missionId": "M-01",
                "deviceId": "V-01",
                "capturedAt": "2026-07-23T09:30:00+09:00",
                "latitude": 37.5,
                "longitude": 127.0,
                "altitude": 15,
                "autoPublish": True,
            },
            "V-default",
        )
        self.assertEqual("req-1", request.request_id)
        self.assertEqual("2026-07-23T00:30:00.000", request.captured_at)

    def test_out_of_range_coordinate_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            InferenceRequest.from_mapping(
                {
                    "requestId": "req-1",
                    "capturedAt": "2026-07-23T09:30:00",
                    "latitude": 95,
                    "longitude": 127,
                },
                "V-01",
            )

    def test_feedback_is_limited_to_shared_judgments(self) -> None:
        with self.assertRaises(ValidationError):
            OperatorFeedback.from_mapping({"requestId": "req-1", "judgment": "delete"})


if __name__ == "__main__":
    unittest.main()

