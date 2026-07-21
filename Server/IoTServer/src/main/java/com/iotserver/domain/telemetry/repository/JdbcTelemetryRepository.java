package com.iotserver.domain.telemetry.repository;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.iotserver.domain.telemetry.entity.DroneTelemetry;
import com.iotserver.domain.telemetry.entity.VehicleTelemetry;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.jdbc.core.BatchPreparedStatementSetter;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.util.List;
import java.util.Map;

@Slf4j
@Repository
@RequiredArgsConstructor
public class JdbcTelemetryRepository {

    private final JdbcTemplate jdbcTemplate;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Transactional
    public void saveAllVehicleTelemetries(List<VehicleTelemetry> telemetries) {
        if (telemetries.isEmpty()) return;

        String sql = "INSERT INTO vehicle_telemetries (vehicle_id, latitude, longitude, altitude, speed, battery_level, pitch, roll, yaw, signal_strength, raw_data, recorded_at) " +
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

        jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {
            @Override
            public void setValues(PreparedStatement ps, int i) throws SQLException {
                VehicleTelemetry telemetry = telemetries.get(i);
                ps.setString(1, telemetry.getVehicle().getId());
                ps.setDouble(2, telemetry.getLatitude());
                ps.setDouble(3, telemetry.getLongitude());
                ps.setDouble(4, telemetry.getAltitude());
                ps.setDouble(5, telemetry.getSpeed());
                ps.setBigDecimal(6, telemetry.getBatteryLevel());
                
                if (telemetry.getPitch() != null) ps.setDouble(7, telemetry.getPitch());
                else ps.setNull(7, java.sql.Types.DOUBLE);

                if (telemetry.getRoll() != null) ps.setDouble(8, telemetry.getRoll());
                else ps.setNull(8, java.sql.Types.DOUBLE);

                if (telemetry.getYaw() != null) ps.setDouble(9, telemetry.getYaw());
                else ps.setNull(9, java.sql.Types.DOUBLE);

                if (telemetry.getSignalStrength() != null) ps.setBigDecimal(10, telemetry.getSignalStrength());
                else ps.setNull(10, java.sql.Types.DECIMAL);

                ps.setString(11, toJsonString(telemetry.getRawData()));
                ps.setTimestamp(12, Timestamp.valueOf(telemetry.getRecordedAt()));
            }

            @Override
            public int getBatchSize() {
                return telemetries.size();
            }
        });
    }

    @Transactional
    public void saveAllDroneTelemetries(List<DroneTelemetry> telemetries) {
        if (telemetries.isEmpty()) return;

        String sql = "INSERT INTO drone_telemetries (drone_id, latitude, longitude, altitude, speed, battery_level, pitch, roll, yaw, signal_strength, raw_data, recorded_at) " +
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

        jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {
            @Override
            public void setValues(PreparedStatement ps, int i) throws SQLException {
                DroneTelemetry telemetry = telemetries.get(i);
                ps.setString(1, telemetry.getDrone().getId());
                ps.setDouble(2, telemetry.getLatitude());
                ps.setDouble(3, telemetry.getLongitude());
                ps.setDouble(4, telemetry.getAltitude());
                ps.setDouble(5, telemetry.getSpeed());
                ps.setBigDecimal(6, telemetry.getBatteryLevel());

                if (telemetry.getPitch() != null) ps.setDouble(7, telemetry.getPitch());
                else ps.setNull(7, java.sql.Types.DOUBLE);

                if (telemetry.getRoll() != null) ps.setDouble(8, telemetry.getRoll());
                else ps.setNull(8, java.sql.Types.DOUBLE);

                if (telemetry.getYaw() != null) ps.setDouble(9, telemetry.getYaw());
                else ps.setNull(9, java.sql.Types.DOUBLE);

                if (telemetry.getSignalStrength() != null) ps.setBigDecimal(10, telemetry.getSignalStrength());
                else ps.setNull(10, java.sql.Types.DECIMAL);

                ps.setString(11, toJsonString(telemetry.getRawData()));
                ps.setTimestamp(12, Timestamp.valueOf(telemetry.getRecordedAt()));
            }

            @Override
            public int getBatchSize() {
                return telemetries.size();
            }
        });
    }

    private String toJsonString(Map<String, Object> rawData) {
        if (rawData == null || rawData.isEmpty()) {
            return null;
        }
        try {
            return objectMapper.writeValueAsString(rawData);
        } catch (JsonProcessingException e) {
            log.warn("Failed to serialize raw_data to JSON String", e);
            return null;
        }
    }
}
