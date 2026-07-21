package com.iotserver.domain.device.entity;

import com.iotserver.global.entity.BaseTimeEntity;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "gateways")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class Gateway extends BaseTimeEntity {

    @Id
    @Column(name = "id", length = 50)
    private String id;

    @Column(name = "name", nullable = false, length = 100)
    private String name;

    @Column(name = "status", nullable = false, length = 20)
    private String status; // online, offline, error

    @Column(name = "ip_address", length = 45)
    private String ipAddress;

    @Column(name = "last_heartbeat_at")
    private LocalDateTime lastHeartbeatAt;
}
