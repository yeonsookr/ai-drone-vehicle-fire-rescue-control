package com.iotserver.domain.telemetry.scheduler;

import com.iotserver.domain.device.entity.Drone;
import com.iotserver.domain.device.entity.Vehicle;
import com.iotserver.domain.telemetry.entity.DroneTelemetry;
import com.iotserver.domain.telemetry.entity.VehicleTelemetry;
import com.iotserver.domain.telemetry.queue.TelemetryQueue;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
public class TelemetrySchedulerTests {

    @Autowired
    private TelemetryQueue telemetryQueue;

    @Autowired
    private TelemetryScheduler telemetryScheduler;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    private static final String VEHICLE_ID = "vehicle-test-id-999";
    private static final String DRONE_ID = "drone-test-id-999";
    private static final String GATEWAY_ID = "gateway-test-id-999";

    @BeforeEach
    public void setUp() {
        // Clean up and insert test data
        jdbcTemplate.execute("SET FOREIGN_KEY_CHECKS = 0");
        jdbcTemplate.execute("TRUNCATE TABLE vehicle_telemetries");
        jdbcTemplate.execute("TRUNCATE TABLE drone_telemetries");
        jdbcTemplate.execute("TRUNCATE TABLE vehicles");
        jdbcTemplate.execute("TRUNCATE TABLE drones");
        jdbcTemplate.execute("TRUNCATE TABLE gateways");
        jdbcTemplate.execute("SET FOREIGN_KEY_CHECKS = 1");

        // Insert Gateway, Vehicle, Drone to pass FK constraints
        jdbcTemplate.update("INSERT INTO gateways (id, name, status, created_at, updated_at) VALUES (?, ?, ?, NOW(), NOW())",
                GATEWAY_ID, "Test Gateway", "online");

        jdbcTemplate.update("INSERT INTO vehicles (id, gateway_id, name, type, status, battery_level, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, NOW(), NOW())",
                VEHICLE_ID, GATEWAY_ID, "Test Vehicle", "mock", "idle", 100.0);

        jdbcTemplate.update("INSERT INTO drones (id, name, type, status, battery_level, created_at, updated_at) VALUES (?, ?, ?, ?, ?, NOW(), NOW())",
                DRONE_ID, "Test Drone", "mock", "docked", 100.0);
    }

    @Test
    public void testHighSpeedTelemetryBulkInsertion() throws Exception {
        // 1. Prepare 200 telemetry items (100 vehicle, 100 drone)
        Map<String, Object> rawData = new HashMap<>();
        rawData.put("temperature", 24.5);
        rawData.put("humidity", 40);

        Vehicle vehicle = Vehicle.builder().id(VEHICLE_ID).build();
        Drone drone = Drone.builder().id(DRONE_ID).build();

        for (int i = 0; i < 100; i++) {
            VehicleTelemetry v = VehicleTelemetry.builder()
                    .vehicle(vehicle)
                    .latitude(37.5 + i * 0.001)
                    .longitude(127.0 + i * 0.001)
                    .altitude(0.0)
                    .speed(10.0 + i)
                    .batteryLevel(BigDecimal.valueOf(90.0))
                    .pitch(0.0)
                    .roll(0.0)
                    .yaw(0.0)
                    .signalStrength(BigDecimal.valueOf(95.0))
                    .rawData(rawData)
                    .recordedAt(LocalDateTime.now())
                    .build();
            telemetryQueue.addVehicleTelemetry(v);

            DroneTelemetry d = DroneTelemetry.builder()
                    .drone(drone)
                    .latitude(37.5 + i * 0.001)
                    .longitude(127.0 + i * 0.001)
                    .altitude(50.0 + i)
                    .speed(15.0 + i)
                    .batteryLevel(BigDecimal.valueOf(80.0))
                    .pitch(0.1)
                    .roll(0.1)
                    .yaw(1.2)
                    .signalStrength(BigDecimal.valueOf(90.0))
                    .rawData(rawData)
                    .recordedAt(LocalDateTime.now())
                    .build();
            telemetryQueue.addDroneTelemetry(d);
        }

        assertThat(telemetryQueue.getVehicleQueueSize()).isEqualTo(100);
        assertThat(telemetryQueue.getDroneQueueSize()).isEqualTo(100);

        // 2. Trigger the scheduler manually to process and bulk insert
        telemetryScheduler.flushVehicleTelemetry();
        telemetryScheduler.flushDroneTelemetry();

        // 3. Since flush methods are async, wait a short moment for background executor to finish
        Thread.sleep(1500);

        // 4. Assert that queues are now empty
        assertThat(telemetryQueue.getVehicleQueueSize()).isEqualTo(0);
        assertThat(telemetryQueue.getDroneQueueSize()).isEqualTo(0);

        // 5. Verify records exist in database
        Integer vehicleTelemetryCount = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM vehicle_telemetries", Integer.class);
        Integer droneTelemetryCount = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM drone_telemetries", Integer.class);

        assertThat(vehicleTelemetryCount).isEqualTo(100);
        assertThat(droneTelemetryCount).isEqualTo(100);
    }
}
