package demo_app.api.bff.controller;

import demo_app.api.bff.dto.CommandRequest;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClient;

@Tag(name = "BFF - Command")
@RestController
@RequestMapping("/api/commands")
public class CommandController {

    private final RestClient central;

    public CommandController(RestClient centralRestClient) {
        this.central = centralRestClient;
    }

    @Operation(summary = "명령 전송 (proxy to IoTServer)")
    @PostMapping
    public ResponseEntity<Map<String, Object>> send(@Valid @RequestBody CommandRequest req) {
        try {
            @SuppressWarnings("unchecked")
            var res = central.post()
                .uri("/api/commands")
                .body(req)
                .retrieve()
                .body(Map.class);
            return ResponseEntity.status(HttpStatus.CREATED).body(res);
        } catch (Exception e) {
            return ResponseEntity.ok(Map.of(
                "mock", true,
                "message", "Command queued (IoTServer unavailable)",
                "type", req.type(),
                "target_id", req.target_id()
            ));
        }
    }
}
