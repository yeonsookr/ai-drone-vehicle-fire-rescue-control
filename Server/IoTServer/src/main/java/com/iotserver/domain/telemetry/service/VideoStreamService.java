package com.iotserver.domain.telemetry.service;

import com.iotserver.domain.mission.entity.Mission;
import com.iotserver.domain.mission.repository.MissionRepository;
import com.iotserver.domain.telemetry.dto.VideoStreamRegisterDto;
import com.iotserver.domain.telemetry.entity.VideoStream;
import com.iotserver.domain.telemetry.repository.VideoStreamRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Slf4j
@Service
@RequiredArgsConstructor
public class VideoStreamService {

    private final VideoStreamRepository videoStreamRepository;
    private final MissionRepository missionRepository;

    @Transactional
    public VideoStream registerOrUpdateStream(VideoStreamRegisterDto dto) {
        Mission mission = null;
        if (dto.getMissionId() != null && !dto.getMissionId().isBlank()) {
            mission = missionRepository.findById(dto.getMissionId()).orElse(null);
        }

        VideoStream videoStream = videoStreamRepository
                .findByDeviceIdAndDeviceType(dto.getDeviceId(), dto.getDeviceType())
                .orElse(null);

        if (videoStream == null) {
            videoStream = VideoStream.builder()
                    .deviceId(dto.getDeviceId())
                    .deviceType(dto.getDeviceType())
                    .streamUrl(dto.getStreamUrl())
                    .status(dto.getStatus())
                    .mission(mission)
                    .startedAt(LocalDateTime.now())
                    .build();
            log.info("Registering new video stream for device: {} type: {}", dto.getDeviceId(), dto.getDeviceType());
        } else {
            videoStream.updateStream(dto.getStreamUrl(), dto.getStatus(), mission);
            log.info("Updating existing video stream for device: {} type: {} status: {}", dto.getDeviceId(), dto.getDeviceType(), dto.getStatus());
        }

        return videoStreamRepository.save(videoStream);
    }
}
