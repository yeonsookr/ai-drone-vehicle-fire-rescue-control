package com.iotserver.domain.device.entity;

import com.iotserver.global.entity.BaseTimeEntity;
import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;

@Entity
@Table(name = "vehicles")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class Vehicle extends BaseTimeEntity {

    @Id
    @Column(name = "id", length = 50)
    private String id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "gateway_id", unique = true)
    private Gateway gateway;

    @Column(name = "name", nullable = false, length = 100)
    private String name;

    @Column(name = "type", nullable = false, length = 20)
    private String type; // real, mock

    @Column(name = "status", nullable = false, length = 20)
    private String status; // idle, moving, stopped, offline

    @Column(name = "battery_level", precision = 5, scale = 2)
    private BigDecimal batteryLevel;

    @Column(name = "current_lat")
    private Double currentLat;

    @Column(name = "current_lng")
    private Double currentLng;

    @Column(name = "current_alt")
    private Double currentAlt;
}
