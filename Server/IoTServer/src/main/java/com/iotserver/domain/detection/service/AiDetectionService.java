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

        // 2. Validate file extension against allowlist (Stored XSS & Malicious upload prevention)
        String originalFilename = file.getOriginalFilename();
        if (originalFilename == null || !originalFilename.contains(".")) {
            throw new IllegalArgumentException("Invalid file name: missing file extension");
        }

        String extension = originalFilename.substring(originalFilename.lastIndexOf(".")).toLowerCase();
        if (!java.util.List.of(".jpg", ".jpeg", ".png").contains(extension)) {
            throw new IllegalArgumentException("Security Violation: Only .jpg, .jpeg, and .png image files are allowed. Received: " + extension);
        }

        // 2-1. Validate declared Content-Type
        String contentType = file.getContentType();
        if (contentType == null || !java.util.List.of("image/jpeg", "image/png").contains(contentType.toLowerCase())) {
            throw new IllegalArgumentException("Security Violation: Content-Type must be image/jpeg or image/png. Received: " + contentType);
        }

        // 2-2. Validate actual file content via magic bytes (extension/Content-Type spoofing prevention)
        validateImageMagicBytes(file);
        
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

    /**
     * 파일의 실제 내용이 JPEG(FF D8 FF) 또는 PNG(89 50 4E 47)인지 매직바이트로 검증한다.
     * 확장자/Content-Type만 이미지로 위장한 악성 파일 업로드를 차단한다.
     */
    private void validateImageMagicBytes(MultipartFile file) throws IOException {
        byte[] header = new byte[4];
        try (java.io.InputStream is = file.getInputStream()) {
            int read = is.read(header);
            if (read < 4) {
                throw new IllegalArgumentException("Security Violation: File is too small to be a valid image.");
            }
        }

        boolean isJpeg = (header[0] & 0xFF) == 0xFF && (header[1] & 0xFF) == 0xD8 && (header[2] & 0xFF) == 0xFF;
        boolean isPng = (header[0] & 0xFF) == 0x89 && (header[1] & 0xFF) == 0x50
                && (header[2] & 0xFF) == 0x4E && (header[3] & 0xFF) == 0x47;

        if (!isJpeg && !isPng) {
            throw new IllegalArgumentException("Security Violation: File content is not a valid JPEG/PNG image.");
        }
    }
}
