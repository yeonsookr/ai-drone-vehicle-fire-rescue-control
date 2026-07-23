package com.iotserver.domain.telemetry.scheduler;

import com.iotserver.domain.telemetry.entity.DroneTelemetry;
import com.iotserver.domain.telemetry.entity.VehicleTelemetry;
import com.iotserver.domain.telemetry.queue.TelemetryQueue;
import com.iotserver.domain.telemetry.repository.JdbcTelemetryRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.util.List;

@Slf4j
@Component
@RequiredArgsConstructor
public class TelemetryScheduler {

    private final TelemetryQueue telemetryQueue;
    private final JdbcTelemetryRepository jdbcTelemetryRepository;
    private final com.iotserver.global.service.PlatformForwardingService platformForwardingService;

    @Async("telemetryTaskExecutor")
    @Scheduled(fixedDelay = 1000)
    public void flushVehicleTelemetry() {
        if (telemetryQueue.getVehicleQueueSize() == 0) {
            return;
        }

        List<VehicleTelemetry> batch = telemetryQueue.drainVehicleQueue();
        log.debug("Drained {} vehicle telemetries for bulk insert", batch.size());

        try {
            jdbcTelemetryRepository.saveAllVehicleTelemetries(batch);
            log.info("Successfully bulk-inserted {} vehicle telemetries", batch.size());
            platformForwardingService.sendVehicleTelemetryBatch(batch);
        } catch (Exception e) {
            log.error("Failed to bulk-insert vehicle telemetries. Re-enqueuing to prevent data loss.", e);
            // Rollback: put back into queue
            telemetryQueue.addAllVehicleTelemetry(batch);
        }
    }

    @Async("telemetryTaskExecutor")
    @Scheduled(fixedDelay = 1000)
    public void flushDroneTelemetry() {
        if (telemetryQueue.getDroneQueueSize() == 0) {
            return;
        }

        List<DroneTelemetry> batch = telemetryQueue.drainDroneQueue();
        log.debug("Drained {} drone telemetries for bulk insert", batch.size());

        try {
            jdbcTelemetryRepository.saveAllDroneTelemetries(batch);
            log.info("Successfully bulk-inserted {} drone telemetries", batch.size());
            platformForwardingService.sendDroneTelemetryBatch(batch);
        } catch (Exception e) {
            log.error("Failed to bulk-insert drone telemetries. Re-enqueuing to prevent data loss.", e);
            // Rollback: put back into queue
            telemetryQueue.addAllDroneTelemetry(batch);
        }
    }
}
