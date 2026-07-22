package com.iotserver.domain.command.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.iotserver.domain.command.dto.CommandRequestDto;
import com.iotserver.domain.command.entity.Command;
import com.iotserver.domain.command.repository.CommandRepository;
import com.iotserver.domain.mission.entity.Mission;
import com.iotserver.domain.mission.repository.MissionRepository;
import com.iotserver.domain.user.entity.User;
import com.iotserver.domain.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.eclipse.paho.client.mqttv3.IMqttClient;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.nio.charset.StandardCharsets;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class CommandService {

    private final CommandRepository commandRepository;
    private final MissionRepository missionRepository;
    private final UserRepository userRepository;
    private final IMqttClient mqttClient;
    private final ObjectMapper objectMapper = new ObjectMapper().registerModule(new JavaTimeModule());

    @Transactional
    public Command executeCommand(CommandRequestDto dto) {
        Mission mission = null;
        if (dto.getMissionId() != null && !dto.getMissionId().isBlank()) {
            mission = missionRepository.findById(dto.getMissionId()).orElse(null);
        }

        User operator = null;
        Integer opId = dto.getOperatorId() != null ? dto.getOperatorId().intValue() : 1;
        operator = userRepository.findById(opId).orElse(null);

        String commandId = "cmd-" + UUID.randomUUID().toString();
        Map<String, Object> parameters = dto.getParameters() != null ? dto.getParameters() : new HashMap<>();

        Command command = Command.builder()
                .id(commandId)
                .mission(mission)
                .targetType(dto.getTargetType())
                .targetId(dto.getTargetId())
                .type(dto.getType())
                .status("ACK")
                .issuer(dto.getIssuer() != null && !dto.getIssuer().isBlank() ? dto.getIssuer() : "operator")
                .operator(operator)
                .parameters(parameters)
                .issuedAt(LocalDateTime.now())
                .expiresAt(LocalDateTime.now().plusSeconds(30))
                .build();

        Command savedCommand = commandRepository.save(command);
        log.info("Saved command to database: {} (status: {})", commandId, savedCommand.getStatus());

        String topic = String.format("%s/%s/command", dto.getTargetType(), dto.getTargetId());
        
        Map<String, Object> payloadMap = new HashMap<>();
        payloadMap.put("command_id", commandId);
        payloadMap.put("type", dto.getType());
        payloadMap.put("parameters", parameters);
        payloadMap.put("issued_at", command.getIssuedAt().toString());

        try {
            String payloadJson = objectMapper.writeValueAsString(payloadMap);
            MqttMessage message = new MqttMessage(payloadJson.getBytes(StandardCharsets.UTF_8));
            message.setQos(1);
            mqttClient.publish(topic, message);
            log.info("Published command to MQTT topic [{}]: {}", topic, payloadJson);
        } catch (Exception e) {
            log.error("Failed to publish command {} to MQTT topic {}", commandId, topic, e);
            throw new RuntimeException("MQTT publication failed, command rolled back", e);
        }

        return savedCommand;
    }
}
