package com.iotserver.domain.telemetry.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.iotserver.domain.device.entity.Drone;
import com.iotserver.domain.device.entity.Vehicle;
import com.iotserver.domain.telemetry.entity.DroneTelemetry;
import com.iotserver.domain.telemetry.entity.VehicleTelemetry;
import com.iotserver.domain.telemetry.queue.TelemetryQueue;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.eclipse.paho.client.mqttv3.IMqttClient;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class MqttSubscriber {

    private final IMqttClient mqttClient;
    private final TelemetryQueue telemetryQueue;
    private final ObjectMapper objectMapper = new ObjectMapper().registerModule(new JavaTimeModule());

    @PostConstruct
    public void subscribeToTelemetry() {
        // wildcards: drone/+/telemetry and vehicle/+/telemetry
        String droneTopic = "drone/+/telemetry";
        String vehicleTopic = "vehicle/+/telemetry";
        String testTopic = "drone/test/telemetry"; // backwards compatibility

        try {
            // Subscribe to drone telemetry
            mqttClient.subscribe(droneTopic, (topic, msg) -> {
                String payload = new String(msg.getPayload());
                String droneId = getDeviceIdFromTopic(topic);
                processDroneTelemetry(droneId, payload);
            });

            // Subscribe to vehicle telemetry
            mqttClient.subscribe(vehicleTopic, (topic, msg) -> {
                String payload = new String(msg.getPayload());
                String vehicleId = getDeviceIdFromTopic(topic);
                processVehicleTelemetry(vehicleId, payload);
            });

            // Subscribe to test topic
            mqttClient.subscribe(testTopic, (topic, msg) -> {
                String payload = new String(msg.getPayload());
                processDroneTelemetry("drone-test-device", payload);
            });

            log.info("MQTT Telemetry Topics Subscribed: {}, {}, {}", droneTopic, vehicleTopic, testTopic);
        } catch (MqttException e) {
            log.error("Failed to subscribe to MQTT telemetry topics", e);
        }
    }

    private String getDeviceIdFromTopic(String topic) {
        // e.g. "drone/D-01/telemetry" -> "D-01"
        String[] parts = topic.split("/");
        if (parts.length >= 2) {
            return parts[1];
        }
        return "unknown";
    }

    @SuppressWarnings("unchecked")
    private void processDroneTelemetry(String droneId, String payload) {
        try {
            Map<String, Object> map = objectMapper.readValue(payload, Map.class);
            
            if (map.get("latitude") == null || map.get("longitude") == null) {
                log.warn("Dropped corrupted drone telemetry for device {}: latitude or longitude missing", droneId);
                return;
            }

            Drone drone = Drone.builder().id(droneId).build();
            
            DroneTelemetry telemetry = DroneTelemetry.builder()
                    .drone(drone)
                    .latitude(getDouble(map.get("latitude")))
                    .longitude(getDouble(map.get("longitude")))
                    .altitude(getDouble(map.get("altitude")))
                    .speed(getDouble(map.get("speed")))
                    .batteryLevel(getBigDecimal(map.get("battery_level")))
                    .pitch(getDouble(map.get("pitch")))
                    .roll(getDouble(map.get("roll")))
                    .yaw(getDouble(map.get("yaw")))
                    .signalStrength(getBigDecimal(map.get("signal_strength")))
                    .rawData((Map<String, Object>) map.get("raw_data"))
                    .recordedAt(getLocalDateTime(map.get("recorded_at")))
                    .build();

            telemetryQueue.addDroneTelemetry(telemetry);
            log.debug("Queued drone telemetry for device: {}", droneId);
        } catch (Exception e) {
            log.warn("Failed to parse or queue drone telemetry payload: {}", payload, e);
        }
    }

    @SuppressWarnings("unchecked")
    private void processVehicleTelemetry(String vehicleId, String payload) {
        try {
            Map<String, Object> map = objectMapper.readValue(payload, Map.class);

            if (map.get("latitude") == null || map.get("longitude") == null) {
                log.warn("Dropped corrupted vehicle telemetry for device {}: latitude or longitude missing", vehicleId);
                return;
            }

            Vehicle vehicle = Vehicle.builder().id(vehicleId).build();

            VehicleTelemetry telemetry = VehicleTelemetry.builder()
                    .vehicle(vehicle)
                    .latitude(getDouble(map.get("latitude")))
                    .longitude(getDouble(map.get("longitude")))
                    .altitude(getDouble(map.get("altitude")))
                    .speed(getDouble(map.get("speed")))
                    .batteryLevel(getBigDecimal(map.get("battery_level")))
                    .pitch(getDouble(map.get("pitch")))
                    .roll(getDouble(map.get("roll")))
                    .yaw(getDouble(map.get("yaw")))
                    .signalStrength(getBigDecimal(map.get("signal_strength")))
                    .rawData((Map<String, Object>) map.get("raw_data"))
                    .recordedAt(getLocalDateTime(map.get("recorded_at")))
                    .build();

            telemetryQueue.addVehicleTelemetry(telemetry);
            log.debug("Queued vehicle telemetry for device: {}", vehicleId);
        } catch (Exception e) {
            log.warn("Failed to parse or queue vehicle telemetry payload: {}", payload, e);
        }
    }

    private Double getDouble(Object obj) {
        if (obj == null) return 0.0;
        if (obj instanceof Number) {
            return ((Number) obj).doubleValue();
        }
        try {
            return Double.parseDouble(obj.toString());
        } catch (NumberFormatException e) {
            return 0.0;
        }
    }

    private BigDecimal getBigDecimal(Object obj) {
        if (obj == null) return BigDecimal.ZERO;
        if (obj instanceof BigDecimal) {
            return (BigDecimal) obj;
        }
        try {
            return new BigDecimal(obj.toString());
        } catch (Exception e) {
            return BigDecimal.ZERO;
        }
    }

    private LocalDateTime getLocalDateTime(Object obj) {
        if (obj == null) return LocalDateTime.now();
        try {
            return LocalDateTime.parse(obj.toString(), DateTimeFormatter.ISO_DATE_TIME);
        } catch (Exception e) {
            try {
                return LocalDateTime.parse(obj.toString(), DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
            } catch (Exception ex) {
                return LocalDateTime.now();
            }
        }
    }
}
