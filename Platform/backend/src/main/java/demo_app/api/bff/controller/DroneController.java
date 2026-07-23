package demo_app.api.bff.controller;

import demo_app.api.bff.dto.CreateDeviceRequest;
import demo_app.api.bff.dto.DroneDto;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestClient;

@Tag(name = "BFF - Drone")
@RestController
@RequestMapping("/api/drones")
public class DroneController {

    private final RestClient central;

    public DroneController(RestClient centralRestClient) {
        this.central = centralRestClient;
    }

    @Operation(summary = "드론 목록 조회")
    @GetMapping
    public List<DroneDto> list() {
        var res = central.get().uri("/api/drones").retrieve().body(DroneDto[].class);
        return res != null ? Arrays.asList(res) : List.of();
    }

    @Operation(summary = "드론 등록 (proxy to IoTServer)")
    @PostMapping
    public ResponseEntity<Map<String, Object>> create(@Valid @RequestBody CreateDeviceRequest req) {
        try {
            @SuppressWarnings("unchecked")
            var res = central.post().uri("/api/drones").body(req).retrieve().body(Map.class);
            return ResponseEntity.status(HttpStatus.CREATED).body(res);
        } catch (Exception e) {
            return ResponseEntity.ok(Map.of("mock", true, "id", req.id(), "status", "created"));
        }
    }

    @Operation(summary = "드론 수정 (proxy to IoTServer)")
    @PutMapping("/{id}")
    public ResponseEntity<Map<String, Object>> update(@PathVariable String id, @Valid @RequestBody CreateDeviceRequest req) {
        try {
            @SuppressWarnings("unchecked")
            var res = central.put().uri("/api/drones/" + id).body(req).retrieve().body(Map.class);
            return ResponseEntity.ok(res);
        } catch (Exception e) {
            return ResponseEntity.ok(Map.of("mock", true, "id", id, "status", "updated"));
        }
    }

    @Operation(summary = "드론 삭제 (proxy to IoTServer)")
    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> delete(@PathVariable String id) {
        try {
            central.delete().uri("/api/drones/" + id).retrieve();
            return ResponseEntity.ok(Map.of("status", "deleted", "id", id));
        } catch (Exception e) {
            return ResponseEntity.ok(Map.of("mock", true, "id", id, "status", "deleted"));
        }
    }
}
