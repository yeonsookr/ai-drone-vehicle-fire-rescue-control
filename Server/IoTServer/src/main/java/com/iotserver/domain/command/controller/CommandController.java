package com.iotserver.domain.command.controller;

import com.iotserver.domain.command.dto.CommandRequestDto;
import com.iotserver.domain.command.entity.Command;
import com.iotserver.domain.command.service.CommandService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/commands")
@RequiredArgsConstructor
public class CommandController {

    private final CommandService commandService;

    @PostMapping
    public ResponseEntity<Command> createCommand(@Valid @RequestBody CommandRequestDto dto) {
        Command command = commandService.executeCommand(dto);
        return ResponseEntity.status(HttpStatus.CREATED).body(command);
    }
}
