package com.iotserver.domain.detection.controller;

import com.iotserver.domain.detection.repository.AiDetectionRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.context.WebApplicationContext;

import java.io.File;
import java.nio.charset.StandardCharsets;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@Transactional
public class AiDetectionControllerTests {

    private MockMvc mockMvc;

    @Autowired
    private WebApplicationContext webApplicationContext;

    @Autowired
    private AiDetectionRepository aiDetectionRepository;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    private static final String VEHICLE_ID = "V-01";
    private static final String GATEWAY_ID = "G-01";
    private static final String DRONE_ID = "D-01";
    private static final String MISSION_ID = "M-01";

    @BeforeEach
    public void setUp() {
        this.mockMvc = MockMvcBuilders.webAppContextSetup(webApplicationContext).build();
        
        jdbcTemplate.execute("SET FOREIGN_KEY_CHECKS = 0");
        jdbcTemplate.execute("TRUNCATE TABLE ai_detections");
        jdbcTemplate.execute("TRUNCATE TABLE missions");
        jdbcTemplate.execute("TRUNCATE TABLE vehicles");
        jdbcTemplate.execute("TRUNCATE TABLE drones");
        jdbcTemplate.execute("TRUNCATE TABLE gateways");
        jdbcTemplate.execute("TRUNCATE TABLE users");
        jdbcTemplate.execute("SET FOREIGN_KEY_CHECKS = 1");

        // Insert Gateway, Vehicle, Drone, User, and Mission to satisfy foreign key constraints
        jdbcTemplate.update("INSERT INTO users (id, username, password_hash, role, created_at, updated_at) VALUES (?, ?, ?, ?, NOW(), NOW())",
                1, "admin", "hash", "admin");

        jdbcTemplate.update("INSERT INTO gateways (id, name, status, created_at, updated_at) VALUES (?, ?, ?, NOW(), NOW())",
                GATEWAY_ID, "Test Gateway", "online");

        jdbcTemplate.update("INSERT INTO vehicles (id, gateway_id, name, type, status, battery_level, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, NOW(), NOW())",
                VEHICLE_ID, GATEWAY_ID, "Test Vehicle", "mock", "idle", 100.0);

        jdbcTemplate.update("INSERT INTO drones (id, name, type, status, battery_level, created_at, updated_at) VALUES (?, ?, ?, ?, ?, NOW(), NOW())",
                DRONE_ID, "Test Drone", "mock", "docked", 100.0);

        jdbcTemplate.update("INSERT INTO missions (id, type, status, vehicle_id, drone_id, created_by, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, NOW(), NOW())",
                MISSION_ID, "patrol", "ASSIGNED", VEHICLE_ID, DRONE_ID, 1);
    }

    @Test
    public void testUploadSnapshotAndSaveDetection() throws Exception {
        // 1. Prepare Mock Image File
        MockMultipartFile imageFile = new MockMultipartFile(
                "file",
                "test_snapshot.jpg",
                "image/jpeg",
                "dummy image content".getBytes(StandardCharsets.UTF_8)
        );

        // 2. Prepare Metadata JSON with the required missionId
        String metadataJson = "{"
                + "\"missionId\": \"" + MISSION_ID + "\","
                + "\"deviceId\": \"" + VEHICLE_ID + "\","
                + "\"deviceType\": \"vehicle\","
                + "\"detectionType\": \"forest_fire\","
                + "\"confidence\": 0.92,"
                + "\"latitude\": 37.52412,"
                + "\"longitude\": 127.02534,"
                + "\"detectedAt\": \"2026-07-22T10:10:00\""
                + "}";

        // 3. Perform multipart request
        mockMvc.perform(multipart("/api/detections/snapshot")
                        .file(imageFile)
                        .param("metadata", metadataJson))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.status").value("success"))
                .andExpect(jsonPath("$.detectionId").exists())
                .andExpect(jsonPath("$.imageUrl").exists());

        // 4. Verify in DB
        var detections = aiDetectionRepository.findAll();
        assertThat(detections).hasSize(1);
        var detection = detections.get(0);
        assertThat(detection.getVehicle().getId()).isEqualTo(VEHICLE_ID);
        assertThat(detection.getDetectionType()).isEqualTo("forest_fire");
        assertThat(detection.getConfidence()).isEqualTo(0.92);
        assertThat(detection.getSnapshotUrl()).startsWith("/uploads/detections/");

        // 5. Clean up local uploaded file to prevent cluttering the workspace
        String savedFilename = detection.getSnapshotUrl().substring(detection.getSnapshotUrl().lastIndexOf("/") + 1);
        File savedFile = new File("uploads/detections/" + savedFilename);
        if (savedFile.exists()) {
            boolean deleted = savedFile.delete();
            System.out.println("Cleaned up mock upload file: " + deleted);
        }
    }
}
