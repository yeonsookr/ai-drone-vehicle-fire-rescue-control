package com.iotserver.domain.command.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.http.MediaType;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;
import org.eclipse.paho.client.mqttv3.IMqttClient;

import java.util.HashMap;
import java.util.Map;

import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.notNullValue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
public class CommandControllerTests {

    private MockMvc mockMvc;

    @Autowired
    private WebApplicationContext webApplicationContext;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @MockitoBean
    private IMqttClient mqttClient;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @BeforeEach
    public void setUp() {
        this.mockMvc = MockMvcBuilders.webAppContextSetup(webApplicationContext).build();

        jdbcTemplate.execute("SET FOREIGN_KEY_CHECKS = 0");
        jdbcTemplate.execute("TRUNCATE TABLE commands");
        jdbcTemplate.execute("TRUNCATE TABLE missions");
        jdbcTemplate.execute("TRUNCATE TABLE users");
        jdbcTemplate.execute("SET FOREIGN_KEY_CHECKS = 1");

        jdbcTemplate.execute("INSERT INTO users (id, username, password_hash, role, created_at, updated_at) " +
                "VALUES (1, 'operator_user', 'hash', 'operator', NOW(), NOW())");
        jdbcTemplate.execute("INSERT INTO missions (id, type, status, created_by, created_at, updated_at) " +
                "VALUES ('M-99', 'patrol', 'ASSIGNED', 1, NOW(), NOW())");
    }

    @Test
    public void testCreateCommand_SuccessAndSnakeCase() throws Exception {
        Map<String, Object> params = new HashMap<>();
        params.put("joystick_x", 0.8);
        params.put("joystick_y", -0.3);

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("mission_id", "M-99");
        requestBody.put("target_type", "drone");
        requestBody.put("target_id", "D-99");
        requestBody.put("type", "manual_control");
        requestBody.put("operator_id", 1);
        requestBody.put("parameters", params);

        mockMvc.perform(post("/api/commands")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(requestBody)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id", notNullValue()))
                .andExpect(jsonPath("$.target_type", is("drone")))
                .andExpect(jsonPath("$.target_id", is("D-99")))
                .andExpect(jsonPath("$.status", is("ACK")))
                .andExpect(jsonPath("$.parameters.joystick_x", is(0.8)))
                .andExpect(jsonPath("$.issued_at", notNullValue()))
                .andExpect(jsonPath("$.expires_at", notNullValue()));

        Mockito.verify(mqttClient, Mockito.times(1))
                .publish(eq("drone/D-99/command"), any());
    }
}
