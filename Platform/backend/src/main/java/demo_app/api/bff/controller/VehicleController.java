package demo_app.api.bff.controller;

import demo_app.api.bff.dto.VehicleDto;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.util.Arrays;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClient;

@Tag(name = "BFF - Vehicle")
@RestController
@RequestMapping("/api/vehicles")
public class VehicleController {

    private final RestClient central;

    public VehicleController(RestClient centralRestClient) {
        this.central = centralRestClient;
    }

    @Operation(summary = "차량 목록 조회")
    @GetMapping
    public List<VehicleDto> list() {
        var res = central.get().uri("/api/vehicles").retrieve().body(VehicleDto[].class);
        return res != null ? Arrays.asList(res) : List.of();
    }
}
