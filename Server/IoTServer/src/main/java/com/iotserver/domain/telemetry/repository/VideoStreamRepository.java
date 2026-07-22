package com.iotserver.domain.telemetry.repository;

import com.iotserver.domain.telemetry.entity.VideoStream;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface VideoStreamRepository extends JpaRepository<VideoStream, Long> {
    Optional<VideoStream> findByDeviceIdAndDeviceType(String deviceId, String deviceType);
}
