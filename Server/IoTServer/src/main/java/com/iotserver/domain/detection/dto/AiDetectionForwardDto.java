package com.iotserver.domain.detection.dto;

import com.iotserver.domain.detection.entity.AiDetection;
import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@Builder
public class AiDetectionForwardDto {
    private String detectionId;
    private String missionId;
    private String deviceId;
    private String deviceType;
    private String detectionType;
    private Double confidence;
    private Double latitude;
    private Double longitude;
    private String imageUrl;
    private LocalDateTime detectedAt;

    public static AiDetectionForwardDto from(AiDetection d) {
        if (d == null) return null;

        String deviceId = null;
        String deviceType = null;
        if (d.getDrone() != null) {
            deviceId = d.getDrone().getId();
            deviceType = "drone";
        } else if (d.getVehicle() != null) {
            deviceId = d.getVehicle().getId();
            deviceType = "vehicle";
        }

        return AiDetectionForwardDto.builder()
                .detectionId(d.getId())
                .missionId(d.getMission() != null ? d.getMission().getId() : null)
                .deviceId(deviceId)
                .deviceType(deviceType)
                .detectionType(d.getDetectionType())
                .confidence(d.getConfidence())
                .latitude(d.getLatitude())
                .longitude(d.getLongitude())
                .imageUrl(d.getSnapshotUrl())
                .detectedAt(d.getDetectedAt())
                .build();
    }
}
