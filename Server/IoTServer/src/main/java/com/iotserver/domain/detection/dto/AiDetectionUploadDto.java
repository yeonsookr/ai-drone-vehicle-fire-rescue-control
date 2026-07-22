package com.iotserver.domain.detection.dto;

import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.*;

import java.time.LocalDateTime;
import java.util.Map;

@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
@ToString
public class AiDetectionUploadDto {

    private String missionId;

    @NotBlank(message = "deviceId is required")
    private String deviceId;

    @NotBlank(message = "deviceType is required")
    private String deviceType;

    @NotBlank(message = "detectionType is required")
    private String detectionType; // forest_fire, smoke, distressed_person

    @NotNull(message = "confidence is required")
    @DecimalMin(value = "0.0", message = "confidence must be >= 0.0")
    @DecimalMax(value = "1.0", message = "confidence must be <= 1.0")
    private Double confidence;

    private Map<String, Object> boundingBox;

    @NotNull(message = "latitude is required")
    private Double latitude;

    @NotNull(message = "longitude is required")
    private Double longitude;

    private Double altitude;

    @NotNull(message = "detectedAt is required")
    private LocalDateTime detectedAt;

    private String modelVersion; // Optional: e.g. "yolov8-orin-v1.0" or "yolov10-server-v2.0"
    
    private String source; // Optional: "edge_ai_orin" or "server_gpu"
}
