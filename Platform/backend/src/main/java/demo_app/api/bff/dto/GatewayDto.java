package demo_app.api.bff.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
public record GatewayDto(
    String id,
    String name,
    String status,
    String ip_address,
    String last_heartbeat_at
) {}
