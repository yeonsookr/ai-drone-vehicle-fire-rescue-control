package com.iotserver.domain.telemetry.service;

import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.eclipse.paho.client.mqttv3.IMqttClient;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class MqttSubscriber {

    private final IMqttClient mqttClient;

    @PostConstruct
    public void subscribeToTelemetry() {
        String topic = "drone/test/telemetry";

        try {
            mqttClient.subscribe(topic, (t, msg) -> {
                String payload = new String(msg.getPayload());

                log.info("[MQTT 임시 수신 테스트] 토픽: {}, 메시지: {}", t, payload);
            });

            log.info("MQTT 임시 토픽 구독 성공: {}", topic);
        } catch (MqttException e) {
            log.error("MQTT 구독 중 에러 발생", e);
        }
    }
}
