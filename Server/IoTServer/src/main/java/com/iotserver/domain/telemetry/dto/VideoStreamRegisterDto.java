package com.iotserver.domain.telemetry.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.*;

@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class VideoStreamRegisterDto {

    @NotBlank(message = "deviceId is required")
    private String deviceId;

    @NotBlank(message = "deviceType is required")
    private String deviceType;

    @NotBlank(message = "streamUrl is required")
    private String streamUrl;

    @NotBlank(message = "status is required")
    private String status;

    private String missionId;
}
