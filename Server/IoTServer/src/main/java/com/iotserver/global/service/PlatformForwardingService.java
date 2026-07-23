package com.iotserver.global.service;

import com.iotserver.domain.detection.dto.AiDetectionForwardDto;
import com.iotserver.domain.detection.entity.AiDetection;
import com.iotserver.domain.telemetry.dto.DroneTelemetryForwardDto;
import com.iotserver.domain.telemetry.dto.VehicleTelemetryForwardDto;
import com.iotserver.domain.telemetry.entity.DroneTelemetry;
import com.iotserver.domain.telemetry.entity.VehicleTelemetry;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Service
public class PlatformForwardingService {

    private RestTemplate restTemplate = new RestTemplate();
    private final String platformServerUrl;

    public PlatformForwardingService(@Value("${app.platform-server-url}") String platformServerUrl) {
        this.platformServerUrl = platformServerUrl;
        log.info("Initializing PlatformForwardingService targeting: {}", platformServerUrl);
    }

    // Package-private setter for unit testing mocking
    void setRestTemplate(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    @Async("telemetryTaskExecutor")
    public void sendDroneTelemetryBatch(List<DroneTelemetry> telemetries) {
        if (telemetries == null || telemetries.isEmpty()) {
            return;
        }

        List<DroneTelemetryForwardDto> dtos = telemetries.stream()
                .map(DroneTelemetryForwardDto::from)
                .collect(Collectors.toList());

        String url = platformServerUrl + "/api/callbacks/telemetry/drone";
        try {
            log.debug("Forwarding {} drone telemetries to platform at {}", dtos.size(), url);
            restTemplate.postForLocation(url, dtos);
            log.info("Successfully forwarded {} drone telemetries to platform", dtos.size());
        } catch (Exception e) {
            log.error("Failed to forward drone telemetry batch to platform at url: {}", url, e);
        }
    }

    @Async("telemetryTaskExecutor")
    public void sendVehicleTelemetryBatch(List<VehicleTelemetry> telemetries) {
        if (telemetries == null || telemetries.isEmpty()) {
            return;
        }

        List<VehicleTelemetryForwardDto> dtos = telemetries.stream()
                .map(VehicleTelemetryForwardDto::from)
                .collect(Collectors.toList());

        String url = platformServerUrl + "/api/callbacks/telemetry/vehicle";
        try {
            log.debug("Forwarding {} vehicle telemetries to platform at {}", dtos.size(), url);
            restTemplate.postForLocation(url, dtos);
            log.info("Successfully forwarded {} vehicle telemetries to platform", dtos.size());
        } catch (Exception e) {
            log.error("Failed to forward vehicle telemetry batch to platform at url: {}", url, e);
        }
    }

    @Async("telemetryTaskExecutor")
    public void sendAiDetectionEvent(AiDetection detection) {
        if (detection == null) {
            return;
        }

        AiDetectionForwardDto dto = AiDetectionForwardDto.from(detection);
        String url = platformServerUrl + "/api/callbacks/detections";
        try {
            log.debug("Forwarding AI detection event {} to platform at {}", dto.getDetectionId(), url);
            restTemplate.postForLocation(url, dto);
            log.info("Successfully forwarded AI detection event {} to platform", dto.getDetectionId());
        } catch (Exception e) {
            log.error("Failed to forward AI detection event {} to platform at url: {}", dto.getDetectionId(), url, e);
        }
    }
}
