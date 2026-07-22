package com.iotserver.domain.detection.repository;

import com.iotserver.domain.detection.entity.AiDetection;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface AiDetectionRepository extends JpaRepository<AiDetection, String> {
}
