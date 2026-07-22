package com.iotserver.domain.command.repository;

import com.iotserver.domain.command.entity.Command;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface CommandRepository extends JpaRepository<Command, String> {
}
