package com.iotserver.domain.device.repository;

import com.iotserver.domain.device.entity.Gateway;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface GatewayRepository extends JpaRepository<Gateway, String> {
}
