package com.iotserver.domain.telemetry.queue;

import com.iotserver.domain.telemetry.entity.DroneTelemetry;
import com.iotserver.domain.telemetry.entity.VehicleTelemetry;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;
import java.util.Queue;
import java.util.concurrent.ConcurrentLinkedQueue;

@Component
public class TelemetryQueue {

    private final Queue<VehicleTelemetry> vehicleQueue = new ConcurrentLinkedQueue<>();
    private final Queue<DroneTelemetry> droneQueue = new ConcurrentLinkedQueue<>();

    public void addVehicleTelemetry(VehicleTelemetry telemetry) {
        vehicleQueue.offer(telemetry);
    }

    public void addDroneTelemetry(DroneTelemetry telemetry) {
        droneQueue.offer(telemetry);
    }

    public List<VehicleTelemetry> drainVehicleQueue() {
        List<VehicleTelemetry> drained = new ArrayList<>();
        VehicleTelemetry item;
        while ((item = vehicleQueue.poll()) != null) {
            drained.add(item);
        }
        return drained;
    }

    public List<DroneTelemetry> drainDroneQueue() {
        List<DroneTelemetry> drained = new ArrayList<>();
        DroneTelemetry item;
        while ((item = droneQueue.poll()) != null) {
            drained.add(item);
        }
        return drained;
    }

    public void addAllVehicleTelemetry(List<VehicleTelemetry> telemetries) {
        vehicleQueue.addAll(telemetries);
    }

    public void addAllDroneTelemetry(List<DroneTelemetry> telemetries) {
        droneQueue.addAll(telemetries);
    }

    public int getVehicleQueueSize() {
        return vehicleQueue.size();
    }

    public int getDroneQueueSize() {
        return droneQueue.size();
    }
}
