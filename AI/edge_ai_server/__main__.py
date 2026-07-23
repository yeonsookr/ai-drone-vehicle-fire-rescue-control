"""Run with: python -m edge_ai_server"""

from __future__ import annotations

import logging

from .api_server import create_server
from .config import Settings
from .mqtt_bridge import build_mqtt_bridge


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    settings = Settings.from_env()
    server = create_server(settings)
    mqtt_bridge = build_mqtt_bridge(settings, server.service, server.pipeline)
    if mqtt_bridge is not None:
        mqtt_bridge.start()
        server.mqtt_bridge = mqtt_bridge
    logging.getLogger("edge_ai_server").info(
        "Jetson edge AI server listening on http://%s:%s (engine=%s, vehicle=%s)",
        settings.host,
        settings.port,
        settings.engine,
        settings.vehicle_id,
    )
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        logging.getLogger("edge_ai_server").info("Shutdown requested")
    finally:
        if mqtt_bridge is not None:
            mqtt_bridge.stop()
        server.shutdown()
        server.server_close()
        server.pipeline.shutdown()
        server.service.shutdown(wait_for_jobs=True)


if __name__ == "__main__":
    main()
