package demo_app.api.health;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;

@Tag(name = "Health")
public interface HealthApi {

    @Operation(summary = "Health Check", description = "서버 상태를 확인합니다.")
    @ApiResponse(responseCode = "200", description = "OK")
    String health();
}
