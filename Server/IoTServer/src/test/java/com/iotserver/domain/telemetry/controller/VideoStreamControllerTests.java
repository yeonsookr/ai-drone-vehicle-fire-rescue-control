package com.iotserver.domain.telemetry.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.iotserver.domain.telemetry.dto.VideoStreamRegisterDto;
import com.iotserver.domain.telemetry.repository.VideoStreamRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.context.WebApplicationContext;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@Transactional
public class VideoStreamControllerTests {

    private MockMvc mockMvc;

    @Autowired
    private WebApplicationContext webApplicationContext;

    @Autowired
    private VideoStreamRepository videoStreamRepository;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    private final ObjectMapper objectMapper = new ObjectMapper();

    private static final String VEHICLE_ID = "vehicle-test-id-999";
    private static final String DRONE_ID = "drone-test-id-999";
    private static final String GATEWAY_ID = "gateway-test-id-999";
    private static final String MISSION_ID = "mission-test-id-999";

    @BeforeEach
    public void setUp() {
        this.mockMvc = MockMvcBuilders.webAppContextSetup(webApplicationContext).build();

        jdbcTemplate.execute("SET FOREIGN_KEY_CHECKS = 0");
        jdbcTemplate.execute("TRUNCATE TABLE video_streams");
        jdbcTemplate.execute("TRUNCATE TABLE missions");
        jdbcTemplate.execute("TRUNCATE TABLE vehicles");
        jdbcTemplate.execute("TRUNCATE TABLE drones");
        jdbcTemplate.execute("TRUNCATE TABLE gateways");
        jdbcTemplate.execute("TRUNCATE TABLE users");
        jdbcTemplate.execute("SET FOREIGN_KEY_CHECKS = 1");

        // Insert mock data to pass foreign key constraints
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
    public void testRegisterVideoStream() throws Exception {
        VideoStreamRegisterDto dto = VideoStreamRegisterDto.builder()
                .deviceId(DRONE_ID)
                .deviceType("drone")
                .streamUrl("http://192.168.0.15:5000/live")
                .status("streaming")
                .missionId(MISSION_ID) // Associate with the mission as required by DB constraints
                .build();

        mockMvc.perform(post("/api/video-streams")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(dto)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.status").value("success"))
                .andExpect(jsonPath("$.streamId").exists());

        // Verify in DB
        var streamOpt = videoStreamRepository.findByDeviceIdAndDeviceType(DRONE_ID, "drone");
        assertThat(streamOpt).isPresent();
        assertThat(streamOpt.get().getStreamUrl()).isEqualTo("http://192.168.0.15:5000/live");
        assertThat(streamOpt.get().getStatus()).isEqualTo("streaming");
    }
}
