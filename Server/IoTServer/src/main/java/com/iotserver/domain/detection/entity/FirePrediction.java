package com.iotserver.domain.detection.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;
import java.util.Map;

@Entity
@Table(name = "fire_predictions")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
@EntityListeners(AuditingEntityListener.class)
public class FirePrediction {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "event_id", nullable = false)
    private AiDetection aiDetection;

    @Column(name = "model_version", nullable = false, length = 50)
    private String modelVersion;

    @Column(name = "weather_wind_speed", nullable = false)
    private Double weatherWindSpeed;

    @Column(name = "weather_wind_direction", nullable = false)
    private Double weatherWindDirection;

    @Column(name = "weather_humidity", nullable = false)
    private Double weatherHumidity;

    @Column(name = "weather_temperature", nullable = false)
    private Double weatherTemperature;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "prediction_polygon", columnDefinition = "json", nullable = false)
    private Map<String, Object> predictionPolygon;

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
}
