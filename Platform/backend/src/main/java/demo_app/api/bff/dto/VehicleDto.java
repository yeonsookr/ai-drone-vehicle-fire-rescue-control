package demo_app.api.bff.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
public record VehicleDto(
    String id,
    String name,
    String status,
    double battery_level,
    double current_lat,
    double current_lng,
    double current_alt
) {}
