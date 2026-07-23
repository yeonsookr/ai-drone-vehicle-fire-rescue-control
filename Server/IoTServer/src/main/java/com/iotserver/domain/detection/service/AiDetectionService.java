package com.iotserver.domain.detection.service;

import com.iotserver.domain.detection.dto.AiDetectionUploadDto;
import com.iotserver.domain.detection.entity.AiDetection;
import com.iotserver.domain.detection.repository.AiDetectionRepository;
import com.iotserver.domain.device.entity.Drone;
import com.iotserver.domain.device.entity.Vehicle;
import com.iotserver.domain.mission.entity.Mission;
import com.iotserver.domain.mission.repository.MissionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.time.LocalDateTime;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class AiDetectionService {

    private final AiDetectionRepository aiDetectionRepository;
    private final MissionRepository missionRepository;
    private final com.iotserver.global.service.PlatformForwardingService platformForwardingService;

    @Value("${app.upload.dir:uploads}")
    private String uploadDir;

    @Transactional
    public AiDetection uploadSnapshotAndSaveDetection(MultipartFile file, AiDetectionUploadDto dto) throws IOException {
        // 1. Ensure upload directory exists
        File targetDir = new File(uploadDir + File.separator + "detections");
        if (!targetDir.exists()) {
            boolean created = targetDir.mkdirs();
            log.info("Created uploads/detections directory: {}", created);
        }

        // 2. Generate unique filename
        String originalFilename = file.getOriginalFilename();
        String extension = "";
        if (originalFilename != null && originalFilename.contains(".")) {
            extension = originalFilename.substring(originalFilename.lastIndexOf("."));
        } else {
            extension = ".jpg"; // fallback extension
        }
        
        String eventId = "det-" + UUID.randomUUID().toString();
        String newFilename = eventId + extension;
        File destinationFile = new File(targetDir, newFilename);
        
        // 3. Save the image file locally
        file.transferTo(destinationFile.getAbsoluteFile());
        log.info("Saved AI detection snapshot to: {}", destinationFile.getAbsolutePath());

        // 4. Resolve the relative URL path for web access
        String snapshotUrl = "/uploads/detections/" + newFilename;

        // 5. Build entities
        Mission mission = null;
        if (dto.getMissionId() != null && !dto.getMissionId().isBlank()) {
            mission = missionRepository.findById(dto.getMissionId()).orElse(null);
        }

        Drone drone = null;
        Vehicle vehicle = null;
        
        // Match device references
        if ("drone".equalsIgnoreCase(dto.getDeviceType())) {
            drone = Drone.builder().id(dto.getDeviceId()).build();
        } else if ("vehicle".equalsIgnoreCase(dto.getDeviceType())) {
            vehicle = Vehicle.builder().id(dto.getDeviceId()).build();
        }

        // Default bounding box if null to prevent column constraint issues
        java.util.Map<String, Object> bbox = dto.getBoundingBox();
        if (bbox == null) {
            bbox = new java.util.HashMap<>();
        }

        String modelVersion = dto.getModelVersion() != null && !dto.getModelVersion().isBlank()
                ? dto.getModelVersion()
                : "yolov8-orin-v1.0";

        String source = dto.getSource() != null && !dto.getSource().isBlank()
                ? dto.getSource()
                : "edge_ai_orin";

        AiDetection detection = AiDetection.builder()
                .id(eventId)
                .mission(mission)
                .drone(drone)
                .vehicle(vehicle)
                .detectionType(dto.getDetectionType())
                .confidence(dto.getConfidence())
                .boundingBox(bbox)
                .latitude(dto.getLatitude())
                .longitude(dto.getLongitude())
                .altitude(dto.getAltitude() != null ? dto.getAltitude() : 0.0)
                .snapshotUrl(snapshotUrl)
                .modelVersion(modelVersion)
                .source(source)
                .operatorJudgment("unconfirmed") // default judgment
                .detectedAt(dto.getDetectedAt())
                .build();

        AiDetection saved = aiDetectionRepository.save(detection);
        platformForwardingService.sendAiDetectionEvent(saved);
        return saved;
    }
}
