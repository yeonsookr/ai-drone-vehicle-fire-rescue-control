package com.iotserver.domain.telemetry.controller;

import com.iotserver.domain.telemetry.dto.VideoStreamRegisterDto;
import com.iotserver.domain.telemetry.entity.VideoStream;
import com.iotserver.domain.telemetry.service.VideoStreamService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/video-streams")
@RequiredArgsConstructor
public class VideoStreamController {

    private final VideoStreamService videoStreamService;

    @PostMapping
    public ResponseEntity<Map<String, Object>> registerStream(@Valid @RequestBody VideoStreamRegisterDto dto) {
        VideoStream stream = videoStreamService.registerOrUpdateStream(dto);

        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("message", "Stream URL registered successfully");
        response.put("streamId", stream.getId());

        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }
}
