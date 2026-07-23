package demo_app.api.bff.dto;

import jakarta.validation.constraints.NotBlank;

public record CommandRequest(
    @NotBlank String target_type,
    @NotBlank String target_id,
    @NotBlank String type,
    String parameters,
    Integer expires_sec
) {}
