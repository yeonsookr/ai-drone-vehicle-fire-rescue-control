package demo_app.api.bff.controller;

import demo_app.api.bff.dto.DroneDto;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.util.Arrays;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
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
}
