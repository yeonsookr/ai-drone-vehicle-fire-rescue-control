package demo_app.api.bff.dto;

import jakarta.validation.constraints.NotBlank;

public record CreateDeviceRequest(
    @NotBlank String id,
    String name,
    String type,
    String status,
    Double battery_level,
    String gateway_id,
    String ip_address
) {}
