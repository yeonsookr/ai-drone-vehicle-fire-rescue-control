package com.iotserver.domain.detection.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.iotserver.domain.detection.dto.AiDetectionUploadDto;
import com.iotserver.domain.detection.entity.AiDetection;
import com.iotserver.domain.detection.service.AiDetectionService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api/detections")
@RequiredArgsConstructor
public class AiDetectionController {

    private final AiDetectionService aiDetectionService;
    private final ObjectMapper objectMapper = new ObjectMapper().registerModule(new JavaTimeModule());

    @PostMapping("/snapshot")
    public ResponseEntity<Map<String, Object>> uploadSnapshot(
            @RequestParam("file") MultipartFile file,
            @RequestParam("metadata") String metadataJson) {
        
        try {
            log.info("Received AI snapshot upload request. Metadata: {}", metadataJson);
            
            // Deserializing metadata JSON string to DTO
            AiDetectionUploadDto dto = objectMapper.readValue(metadataJson, AiDetectionUploadDto.class);
            
            // Process snapshot and DB save
            AiDetection detection = aiDetectionService.uploadSnapshotAndSaveDetection(file, dto);

            Map<String, Object> response = new HashMap<>();
            response.put("status", "success");
            response.put("message", "AI detection snapshot uploaded successfully");
            response.put("detectionId", detection.getId());
            response.put("imageUrl", detection.getSnapshotUrl());

            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } catch (IOException e) {
            log.error("Failed to save snapshot file", e);
            Map<String, Object> response = new HashMap<>();
            response.put("status", "error");
            response.put("message", "Failed to save file: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        } catch (Exception e) {
            log.error("Invalid metadata format", e);
            Map<String, Object> response = new HashMap<>();
            response.put("status", "error");
            response.put("message", "Invalid metadata JSON payload: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
        }
    }
}
