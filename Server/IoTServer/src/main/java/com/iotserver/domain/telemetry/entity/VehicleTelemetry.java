package com.iotserver.domain.telemetry.entity;

import com.iotserver.domain.device.entity.Vehicle;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Map;

@Entity
@Table(name = "vehicle_telemetries")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class VehicleTelemetry {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "vehicle_id", nullable = false)
    private Vehicle vehicle;

    @Column(name = "latitude", nullable = false)
    private Double latitude;

    @Column(name = "longitude", nullable = false)
    private Double longitude;

    @Column(name = "altitude", nullable = false)
    private Double altitude;

    @Column(name = "speed", nullable = false)
    private Double speed;

    @Column(name = "battery_level", precision = 5, scale = 2, nullable = false)
    private BigDecimal batteryLevel;

    @Column(name = "pitch")
    private Double pitch;

    @Column(name = "roll")
    private Double roll;

    @Column(name = "yaw")
    private Double yaw;

    @Column(name = "signal_strength", precision = 5, scale = 2)
    private BigDecimal signalStrength;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "raw_data", columnDefinition = "json")
    private Map<String, Object> rawData;

    @Column(name = "recorded_at", nullable = false)
    private LocalDateTime recordedAt;
}
