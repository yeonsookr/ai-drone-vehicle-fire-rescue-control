package com.iotserver.domain.mission.entity;

import com.iotserver.domain.device.entity.Drone;
import com.iotserver.domain.device.entity.Vehicle;
import com.iotserver.domain.report.entity.ExternalReport;
import com.iotserver.domain.user.entity.User;
import com.iotserver.global.entity.BaseTimeEntity;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "missions")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class Mission extends BaseTimeEntity {

    @Id
    @Column(name = "id", length = 50)
    private String id;

    @Column(name = "type", nullable = false, length = 20)
    private String type; // patrol, dispatch, fire_response

    @Column(name = "status", nullable = false, length = 20)
    private String status; // CREATED, ASSIGNED, DISPATCHED, IN_PROGRESS, COMPLETED, PAUSED, RETURNING, FAILED, CANCELLED

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "vehicle_id")
    private Vehicle vehicle;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "drone_id")
    private Drone drone;

    @Column(name = "assigned_at")
    private LocalDateTime assignedAt;

    @Column(name = "started_at")
    private LocalDateTime startedAt;

    @Column(name = "completed_at")
    private LocalDateTime completedAt;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "created_by")
    private User createdBy;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "external_report_id")
    private ExternalReport externalReport;
}

