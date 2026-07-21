package com.iotserver.domain.telemetry.entity;

import com.iotserver.domain.mission.entity.Mission;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "video_streams")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class VideoStream {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "mission_id")
    private Mission mission;

    @Column(name = "device_type", nullable = false, length = 20)
    private String deviceType; // vehicle, drone

    @Column(name = "device_id", nullable = false, length = 50)
    private String deviceId;

    @Column(name = "stream_url", nullable = false, length = 255)
    private String streamUrl;

    @Column(name = "status", nullable = false, length = 20)
    private String status; // streaming, inactive, error

    @Column(name = "started_at")
    private LocalDateTime startedAt;

    @Column(name = "ended_at")
    private LocalDateTime endedAt;
}
