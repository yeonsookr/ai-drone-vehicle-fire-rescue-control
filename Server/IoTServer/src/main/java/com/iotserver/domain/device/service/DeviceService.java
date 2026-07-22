package com.iotserver.domain.device.service;

import com.iotserver.domain.device.entity.Drone;
import com.iotserver.domain.device.entity.Gateway;
import com.iotserver.domain.device.repository.DroneRepository;
import com.iotserver.domain.device.repository.GatewayRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class DeviceService {

    private final DroneRepository droneRepository;
    private final GatewayRepository gatewayRepository;

    public List<Drone> getAllDrones() {
        return droneRepository.findAll();
    }

    public List<Gateway> getAllGateways() {
        return gatewayRepository.findAll();
    }
}
