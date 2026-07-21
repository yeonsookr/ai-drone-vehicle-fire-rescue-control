package com.iotserver.domain.detection.entity;

import com.iotserver.domain.device.entity.Drone;
import com.iotserver.domain.device.entity.Vehicle;
import com.iotserver.domain.mission.entity.Mission;
import com.iotserver.domain.user.entity.User;
import com.iotserver.global.entity.BaseTimeEntity;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;
import java.util.Map;

@Entity
@Table(name = "ai_detections")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class AiDetection extends BaseTimeEntity {

    @Id
    @Column(name = "id", length = 50)
    private String id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "mission_id", nullable = false)
    private Mission mission;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "drone_id")
    private Drone drone;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "vehicle_id")
    private Vehicle vehicle;

    @Column(name = "detection_type", nullable = false, length = 50)
    private String detectionType; // forest_fire, smoke, distressed_person

    @Column(name = "confidence", nullable = false)
    private Double confidence;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "bounding_box", columnDefinition = "json")
    private Map<String, Object> boundingBox;

    @Column(name = "latitude", nullable = false)
    private Double latitude;

    @Column(name = "longitude", nullable = false)
    private Double longitude;

    @Column(name = "altitude", nullable = false)
    private Double altitude;

    @Column(name = "snapshot_url", length = 255)
    private String snapshotUrl;

    @Column(name = "model_version", nullable = false, length = 50)
    private String modelVersion;

    @Column(name = "source", nullable = false, length = 50)
    private String source; // edge_ai_orin, server_gpu

    @Column(name = "operator_judgment", nullable = false, length = 20)
    private String operatorJudgment; // unconfirmed, approved, false_alarm, pending

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "operator_id")
    private User operator;

    @Column(name = "judged_at")
    private LocalDateTime judgedAt;

    @Column(name = "judgment_reason", columnDefinition = "TEXT")
    private String judgmentReason;

    @Column(name = "detected_at", nullable = false)
    private LocalDateTime detectedAt;
}
