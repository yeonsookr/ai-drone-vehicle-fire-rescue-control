package com.iotserver.domain.command.entity;

import com.iotserver.domain.mission.entity.Mission;
import com.iotserver.domain.user.entity.User;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Entity
@Table(name = "commands")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class Command {

    @Id
    @Column(name = "id", length = 50)
    private String id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "parent_command_id")
    private Command parentCommand;

    @Builder.Default
    @OneToMany(mappedBy = "parentCommand", cascade = CascadeType.ALL)
    private List<Command> childCommands = new ArrayList<>();

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "mission_id")
    private Mission mission;

    @Column(name = "target_type", nullable = false, length = 20)
    private String targetType; // vehicle, drone

    @Column(name = "target_id", nullable = false, length = 50)
    private String targetId;

    @Column(name = "type", nullable = false, length = 50)
    private String type; // move, return, stop, pause

    @Column(name = "status", nullable = false, length = 20)
    private String status; // ACK, RUNNING, SUCCEEDED, FAILED, EXPIRED

    @Column(name = "issuer", nullable = false, length = 50)
    private String issuer; // operator, edge_ai, safety_policy

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "operator_id")
    private User operator;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "parameters", columnDefinition = "json")
    private Map<String, Object> parameters;

    @Column(name = "error_reason", columnDefinition = "TEXT")
    private String errorReason;

    @Column(name = "issued_at", nullable = false)
    private LocalDateTime issuedAt;

    @Column(name = "expires_at", nullable = false)
    private LocalDateTime expiresAt;

    @Column(name = "completed_at")
    private LocalDateTime completedAt;
}
