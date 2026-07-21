package demo_app.api.bff.controller;

import demo_app.api.bff.dto.GatewayDto;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.util.Arrays;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClient;

@Tag(name = "BFF - Gateway")
@RestController
@RequestMapping("/api/gateways")
public class GatewayController {

    private final RestClient central;

    public GatewayController(RestClient centralRestClient) {
        this.central = centralRestClient;
    }

    @Operation(summary = "게이트웨이 목록 조회")
    @GetMapping
    public List<GatewayDto> list() {
        var res = central.get().uri("/api/gateways").retrieve().body(GatewayDto[].class);
        return res != null ? Arrays.asList(res) : List.of();
    }
}
