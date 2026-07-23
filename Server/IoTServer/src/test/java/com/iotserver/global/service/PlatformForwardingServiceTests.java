package com.iotserver.global.service;

import com.iotserver.domain.detection.entity.AiDetection;
import com.iotserver.domain.telemetry.entity.DroneTelemetry;
import com.iotserver.domain.telemetry.entity.VehicleTelemetry;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.web.client.RestTemplate;

import java.util.Collections;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;

class PlatformForwardingServiceTests {

    private RestTemplate restTemplate;
    private PlatformForwardingService platformForwardingService;

    @BeforeEach
    void setUp() {
        restTemplate = Mockito.mock(RestTemplate.class);
        platformForwardingService = new PlatformForwardingService("http://localhost:8081");
        platformForwardingService.setRestTemplate(restTemplate);
    }

    @Test
    void testSendDroneTelemetryBatch() {
        DroneTelemetry telemetry = DroneTelemetry.builder()
                .latitude(37.5)
                .longitude(127.0)
                .build();

        platformForwardingService.sendDroneTelemetryBatch(Collections.singletonList(telemetry));

        verify(restTemplate).postForLocation(eq("http://localhost:8081/api/callbacks/telemetry/drone"), any(List.class));
    }

    @Test
    void testSendVehicleTelemetryBatch() {
        VehicleTelemetry telemetry = VehicleTelemetry.builder()
                .latitude(37.5)
                .longitude(127.0)
                .build();

        platformForwardingService.sendVehicleTelemetryBatch(Collections.singletonList(telemetry));

        verify(restTemplate).postForLocation(eq("http://localhost:8081/api/callbacks/telemetry/vehicle"), any(List.class));
    }

    @Test
    void testSendAiDetectionEvent() {
        AiDetection detection = AiDetection.builder()
                .id("det-123")
                .detectionType("fire")
                .confidence(0.9)
                .build();

        platformForwardingService.sendAiDetectionEvent(detection);

        verify(restTemplate).postForLocation(eq("http://localhost:8081/api/callbacks/detections"), any());
    }
}
