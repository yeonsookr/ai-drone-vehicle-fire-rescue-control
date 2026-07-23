package com.iotserver.domain.telemetry.dto;

import com.iotserver.domain.telemetry.entity.VehicleTelemetry;
import lombok.Builder;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@Builder
public class VehicleTelemetryForwardDto {
    private String vehicleId;
    private Double latitude;
    private Double longitude;
    private Double altitude;
    private Double speed;
    private BigDecimal batteryLevel;
    private Double pitch;
    private Double roll;
    private Double yaw;
    private BigDecimal signalStrength;
    private LocalDateTime recordedAt;

    public static VehicleTelemetryForwardDto from(VehicleTelemetry t) {
        if (t == null) return null;
        return VehicleTelemetryForwardDto.builder()
                .vehicleId(t.getVehicle() != null ? t.getVehicle().getId() : null)
                .latitude(t.getLatitude())
                .longitude(t.getLongitude())
                .altitude(t.getAltitude())
                .speed(t.getSpeed())
                .batteryLevel(t.getBatteryLevel())
                .pitch(t.getPitch())
                .roll(t.getRoll())
                .yaw(t.getYaw())
                .signalStrength(t.getSignalStrength())
                .recordedAt(t.getRecordedAt())
                .build();
    }
}
