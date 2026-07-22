package com.iotserver.domain.command.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CommandRequestDto {

    private String missionId;

    @NotBlank(message = "target_type cannot be blank")
    private String targetType;

    @NotBlank(message = "target_id cannot be blank")
    private String targetId;

    @NotBlank(message = "type cannot be blank")
    private String type;

    private String issuer; // defaults to "operator"

    private Long operatorId;

    private Map<String, Object> parameters;
}
