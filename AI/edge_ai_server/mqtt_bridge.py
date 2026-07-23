"""MQTT control, ACK, AI metadata and status bridge."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta
import json
import logging
import threading
from typing import Any, Callable, Mapping, Protocol, Sequence

from .config import Settings
from .models import BackendCommand, OperatorFeedback, utc_now_iso
from .pipeline import ContinuousInferencePipeline, PipelineEventSink
from .service import EdgeAiService


LOGGER = logging.getLogger("edge_ai_server.mqtt")
MessageCallback = Callable[[str, bytes], None]


class MqttTransport(Protocol):
    def start(self, subscriptions: Sequence[tuple[str, int]], callback: MessageCallback) -> None: ...

    def publish(self, topic: str, payload: bytes, qos: int, retain: bool = False) -> None: ...

    def stop(self) -> None: ...

    def status(self) -> Mapping[str, Any]: ...


class PahoMqttTransport:
    """Paho adapter loaded only when MQTT is enabled on the Jetson."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: Any = None
        self._mqtt: Any = None
        self._subscriptions: Sequence[tuple[str, int]] = ()
        self._callback: MessageCallback | None = None
        self._connected = False
        self._last_error: str | None = None

    def start(self, subscriptions: Sequence[tuple[str, int]], callback: MessageCallback) -> None:
        try:
            import paho.mqtt.client as mqtt  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError(
                "MQTT_ENABLED=true requires paho-mqtt; install edge_ai_server/requirements.txt"
            ) from exc

        self._mqtt = mqtt
        self._subscriptions = subscriptions
        self._callback = callback
        client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=self._settings.mqtt_client_id,
            protocol=mqtt.MQTTv311,
        )
        if self._settings.mqtt_username:
            client.username_pw_set(self._settings.mqtt_username, self._settings.mqtt_password)
        if self._settings.mqtt_tls_enabled:
            client.tls_set()
        client.reconnect_delay_set(min_delay=1, max_delay=30)
        client.on_connect = self._on_connect
        client.on_disconnect = self._on_disconnect
        client.on_message = self._on_message
        self._client = client
        client.connect_async(
            self._settings.mqtt_host,
            self._settings.mqtt_port,
            self._settings.mqtt_keepalive_seconds,
        )
        client.loop_start()

    def _on_connect(
        self,
        client: Any,
        userdata: Any,
        flags: Any,
        reason_code: Any,
        properties: Any,
    ) -> None:
        del userdata, flags, properties
        if reason_code != 0:
            self._last_error = f"MQTT connection rejected: {reason_code}"
            LOGGER.error(self._last_error)
            return
        self._connected = True
        self._last_error = None
        for topic, qos in self._subscriptions:
            client.subscribe(topic, qos=qos)
        LOGGER.info("Connected to MQTT broker and subscribed to %s topics", len(self._subscriptions))

    def _on_disconnect(
        self,
        client: Any,
        userdata: Any,
        disconnect_flags: Any,
        reason_code: Any,
        properties: Any,
    ) -> None:
        del client, userdata, disconnect_flags, properties
        self._connected = False
        if reason_code != 0:
            self._last_error = f"unexpected MQTT disconnect: {reason_code}"
            LOGGER.warning(self._last_error)

    def _on_message(self, client: Any, userdata: Any, message: Any) -> None:
        del client, userdata
        if self._callback is not None:
            self._callback(str(message.topic), bytes(message.payload))

    def publish(self, topic: str, payload: bytes, qos: int, retain: bool = False) -> None:
        if self._client is None or self._mqtt is None:
            raise RuntimeError("MQTT transport is not started")
        result = self._client.publish(topic, payload=payload, qos=qos, retain=retain)
        if result.rc != self._mqtt.MQTT_ERR_SUCCESS:
            self._last_error = f"MQTT publish failed with rc={result.rc}"
            raise RuntimeError(self._last_error)

    def stop(self) -> None:
        if self._client is None:
            return
        try:
            self._client.disconnect()
        finally:
            self._client.loop_stop()
        self._connected = False

    def status(self) -> Mapping[str, Any]:
        return {
            "transport": "paho-mqtt",
            "connected": self._connected,
            "host": self._settings.mqtt_host,
            "port": self._settings.mqtt_port,
            "clientId": self._settings.mqtt_client_id,
            "tls": self._settings.mqtt_tls_enabled,
            "lastError": self._last_error,
        }


class EdgeMqttBridge(PipelineEventSink):
    def __init__(
        self,
        settings: Settings,
        service: EdgeAiService,
        pipeline: ContinuousInferencePipeline,
        transport: MqttTransport,
    ) -> None:
        self._settings = settings
        self._service = service
        self._pipeline = pipeline
        self._transport = transport
        prefix = f"vehicle/{settings.vehicle_id}/ai"
        self.backend_command_topic = f"vehicle/{settings.vehicle_id}/command"
        self.command_topic = f"{prefix}/command"
        self.feedback_topic = f"{prefix}/feedback"
        self.event_topic = f"{prefix}/events"
        self.status_topic = f"{prefix}/status"
        self._command_status_prefix = f"{prefix}/command"
        self._feedback_status_prefix = f"{prefix}/feedback"
        self._stop = threading.Event()
        self._pending: deque[tuple[str, bytes, int, bool]] = deque(maxlen=settings.publish_queue_size)
        self._publish_lock = threading.Lock()
        self._heartbeat: threading.Thread | None = None
        self._started = False

    def start(self) -> None:
        if self._started:
            return
        self._pipeline.set_event_sink(self)
        self._transport.start(
            [
                (self.backend_command_topic, self._settings.mqtt_qos),
                (self.command_topic, self._settings.mqtt_qos),
                (self.feedback_topic, self._settings.mqtt_qos),
            ],
            self._on_message,
        )
        self._started = True
        self._publish_status("online", retain=True)
        self._heartbeat = threading.Thread(
            target=self._heartbeat_loop,
            name="edge-ai-mqtt-heartbeat",
            daemon=True,
        )
        self._heartbeat.start()

    def _on_message(self, topic: str, payload_bytes: bytes) -> None:
        try:
            payload = json.loads(payload_bytes.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("MQTT payload must be a JSON object")
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            self._publish_protocol_error(topic, "MQTT_INVALID_JSON", str(exc))
            return

        if topic in {self.backend_command_topic, self.command_topic}:
            self._handle_command(payload)
        elif topic == self.feedback_topic:
            self._handle_feedback(payload)

    def _handle_command(self, payload: dict[str, Any]) -> None:
        payload.setdefault("targetId", self._settings.vehicle_id)
        if not payload.get("expiresAt") and not payload.get("expires_at"):
            issued_at = payload.get("issuedAt") or payload.get("issued_at")
            if issued_at:
                try:
                    issued = datetime.fromisoformat(str(issued_at).replace("Z", "+00:00"))
                    payload["expiresAt"] = (
                        issued + timedelta(seconds=self._settings.mqtt_command_default_ttl_seconds)
                    ).isoformat()
                except ValueError:
                    # BackendCommand will return the contract validation error.
                    pass
        command_id = str(payload.get("commandId") or payload.get("command_id") or "unknown")
        try:
            command = BackendCommand.from_mapping(payload)
            self._pipeline.submit_command(command)
        except Exception as exc:
            self._publish_json(
                f"{self._command_status_prefix}/{command_id}/status",
                {
                    "schemaVersion": "1.0",
                    "commandId": command_id,
                    "targetId": self._settings.vehicle_id,
                    "status": "FAILED",
                    "errorReason": str(exc),
                    "timestamp": utc_now_iso(),
                },
            )

    def _handle_feedback(self, payload: dict[str, Any]) -> None:
        request_id = str(payload.get("requestId") or payload.get("request_id") or "unknown")
        try:
            feedback = OperatorFeedback.from_mapping(payload)
            stored = self._service.record_feedback(feedback)
            response = {
                "schemaVersion": "1.0",
                "requestId": feedback.request_id,
                "status": "ACK",
                "feedback": stored,
                "timestamp": utc_now_iso(),
            }
        except Exception as exc:
            response = {
                "schemaVersion": "1.0",
                "requestId": request_id,
                "status": "FAILED",
                "errorReason": str(exc),
                "timestamp": utc_now_iso(),
            }
        self._publish_json(f"{self._feedback_status_prefix}/{request_id}/status", response)

    def on_command_update(self, command: Mapping[str, Any]) -> None:
        command_id = str(command.get("commandId", "unknown"))
        payload = dict(command)
        payload["schemaVersion"] = "1.0"
        payload["timestamp"] = utc_now_iso()
        self._publish_json(f"{self._command_status_prefix}/{command_id}/status", payload)

    def on_ai_event(self, event: Mapping[str, Any]) -> None:
        self._publish_json(self.event_topic, event)

    def _heartbeat_loop(self) -> None:
        while not self._stop.wait(self._settings.mqtt_status_interval_seconds):
            self._flush_pending()
            self._publish_status("online", retain=True)

    def _publish_status(self, state: str, retain: bool) -> None:
        self._publish_json(
            self.status_topic,
            {
                "schemaVersion": "1.0",
                "vehicleId": self._settings.vehicle_id,
                "state": state,
                "service": self._service.status(),
                "pipeline": self._pipeline.status(),
                "mqtt": dict(self._transport.status()),
                "timestamp": utc_now_iso(),
            },
            retain=retain,
        )

    def _publish_protocol_error(self, source_topic: str, code: str, message: str) -> None:
        self._publish_json(
            self.status_topic,
            {
                "schemaVersion": "1.0",
                "vehicleId": self._settings.vehicle_id,
                "state": "warning",
                "errorCode": code,
                "message": message,
                "sourceTopic": source_topic,
                "timestamp": utc_now_iso(),
            },
        )

    def _publish_json(self, topic: str, payload: Mapping[str, Any], retain: bool = False) -> None:
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        try:
            self._transport.publish(topic, encoded, qos=self._settings.mqtt_qos, retain=retain)
        except Exception as exc:
            LOGGER.warning("MQTT publish queued after transport failure on %s: %s", topic, exc)
            with self._publish_lock:
                self._pending.append((topic, encoded, self._settings.mqtt_qos, retain))

    def _flush_pending(self) -> None:
        while True:
            with self._publish_lock:
                if not self._pending:
                    return
                item = self._pending.popleft()
            try:
                self._transport.publish(item[0], item[1], qos=item[2], retain=item[3])
            except Exception:
                with self._publish_lock:
                    self._pending.appendleft(item)
                return

    def status(self) -> Mapping[str, Any]:
        with self._publish_lock:
            pending_messages = len(self._pending)
        return {
            "enabled": True,
            "started": self._started,
            "backendCommandTopic": self.backend_command_topic,
            "commandTopic": self.command_topic,
            "feedbackTopic": self.feedback_topic,
            "eventTopic": self.event_topic,
            "statusTopic": self.status_topic,
            "pendingMessages": pending_messages,
            "transport": dict(self._transport.status()),
        }

    def stop(self) -> None:
        if not self._started:
            return
        self._stop.set()
        if self._heartbeat is not None:
            self._heartbeat.join(timeout=2)
        try:
            self._publish_status("offline", retain=True)
        finally:
            self._pipeline.set_event_sink(None)
            self._transport.stop()
            self._started = False


def build_mqtt_bridge(
    settings: Settings,
    service: EdgeAiService,
    pipeline: ContinuousInferencePipeline,
) -> EdgeMqttBridge | None:
    if not settings.mqtt_enabled:
        return None
    return EdgeMqttBridge(
        settings=settings,
        service=service,
        pipeline=pipeline,
        transport=PahoMqttTransport(settings),
    )
