package com.iotserver.domain.device.controller;

import com.iotserver.domain.device.entity.Drone;
import com.iotserver.domain.device.entity.Gateway;
import com.iotserver.domain.device.service.DeviceService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class DeviceController {

    private final DeviceService deviceService;

    @GetMapping("/drones")
    public ResponseEntity<List<Drone>> getDrones() {
        List<Drone> drones = deviceService.getAllDrones();
        return ResponseEntity.ok(drones);
    }

    @GetMapping("/gateways")
    public ResponseEntity<List<Gateway>> getGateways() {
        List<Gateway> gateways = deviceService.getAllGateways();
        return ResponseEntity.ok(gateways);
    }
}
