package com.iotserver.domain.detection.service;

import com.iotserver.domain.detection.dto.AiDetectionUploadDto;
import com.iotserver.domain.detection.repository.AiDetectionRepository;
import com.iotserver.domain.mission.repository.MissionRepository;
import com.iotserver.global.service.PlatformForwardingService;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.mock.web.MockMultipartFile;

public class AiDetectionServiceSecurityTests {

    private AiDetectionRepository aiDetectionRepository;
    private MissionRepository missionRepository;
    private PlatformForwardingService platformForwardingService;
    private AiDetectionService aiDetectionService;

    @BeforeEach
    void setUp() {
        aiDetectionRepository = Mockito.mock(AiDetectionRepository.class);
        missionRepository = Mockito.mock(MissionRepository.class);
        platformForwardingService = Mockito.mock(PlatformForwardingService.class);
        aiDetectionService = new AiDetectionService(aiDetectionRepository, missionRepository, platformForwardingService);
    }

    @Test
    void testUploadSnapshot_RejectsHtmlFile_StoredXSSPrevention() {
        MockMultipartFile htmlFile = new MockMultipartFile(
                "file",
                "malicious_script.html",
                "text/html",
                "<script>alert('XSS')</script>".getBytes()
        );

        AiDetectionUploadDto dto = AiDetectionUploadDto.builder()
                .deviceId("V-01")
                .deviceType("vehicle")
                .detectionType("forest_fire")
                .confidence(0.95)
                .latitude(37.5)
                .longitude(127.0)
                .build();

        Assertions.assertThrows(IllegalArgumentException.class, () -> {
            aiDetectionService.uploadSnapshotAndSaveDetection(htmlFile, dto);
        });
    }

    @Test
    void testUploadSnapshot_RejectsExecutableFile() {
        MockMultipartFile exeFile = new MockMultipartFile(
                "file",
                "malicious.exe",
                "application/octet-stream",
                "MZ...dummy binary".getBytes()
        );

        AiDetectionUploadDto dto = AiDetectionUploadDto.builder()
                .deviceId("V-01")
                .deviceType("vehicle")
                .detectionType("forest_fire")
                .confidence(0.95)
                .latitude(37.5)
                .longitude(127.0)
                .build();

        Assertions.assertThrows(IllegalArgumentException.class, () -> {
            aiDetectionService.uploadSnapshotAndSaveDetection(exeFile, dto);
        });
    }
}
