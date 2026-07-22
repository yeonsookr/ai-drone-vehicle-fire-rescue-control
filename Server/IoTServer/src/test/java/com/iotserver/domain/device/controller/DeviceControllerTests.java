package com.iotserver.domain.device.controller;

import com.iotserver.domain.device.entity.Drone;
import com.iotserver.domain.device.entity.Gateway;
import com.iotserver.domain.device.service.DeviceService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;

import java.math.BigDecimal;
import java.util.List;

import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.is;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
public class DeviceControllerTests {

    private MockMvc mockMvc;

    @Autowired
    private WebApplicationContext webApplicationContext;

    @MockitoBean
    private DeviceService deviceService;

    @BeforeEach
    public void setUp() {
        this.mockMvc = MockMvcBuilders.webAppContextSetup(webApplicationContext).build();
    }

    @Test
    public void testGetDrones_SuccessAndSnakeCase() throws Exception {
        Drone drone = Drone.builder()
                .id("D-01")
                .name("Test Drone")
                .type("real")
                .status("docked")
                .batteryLevel(new BigDecimal("95.50"))
                .currentLat(37.5665)
                .currentLng(126.9780)
                .currentAlt(15.0)
                .build();

        Mockito.when(deviceService.getAllDrones()).thenReturn(List.of(drone));

        mockMvc.perform(get("/api/drones")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].id", is("D-01")))
                .andExpect(jsonPath("$[0].name", is("Test Drone")))
                .andExpect(jsonPath("$[0].battery_level", is(95.50)))
                .andExpect(jsonPath("$[0].current_lat", is(37.5665)))
                .andExpect(jsonPath("$[0].current_lng", is(126.9780)))
                .andExpect(jsonPath("$[0].current_alt", is(15.0)));
    }

    @Test
    public void testGetGateways_SuccessAndSnakeCase() throws Exception {
        Gateway gateway = Gateway.builder()
                .id("G-01")
                .name("Test Gateway")
                .status("online")
                .ipAddress("192.168.0.1")
                .build();

        Mockito.when(deviceService.getAllGateways()).thenReturn(List.of(gateway));

        mockMvc.perform(get("/api/gateways")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].id", is("G-01")))
                .andExpect(jsonPath("$[0].name", is("Test Gateway")))
                .andExpect(jsonPath("$[0].status", is("online")))
                .andExpect(jsonPath("$[0].ip_address", is("192.168.0.1")));
    }
}
