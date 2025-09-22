package com.believer.licar.transport.controller;

import com.believer.licar.transport.dto.TransportCreateRequest;
import com.believer.licar.transport.dto.TransportDetailResponse;
import com.believer.licar.transport.dto.TransportSimpleResponse;
import com.believer.licar.transport.service.TransportService;
import com.believer.licar.prescription.dto.DrugResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/transports")
@RequiredArgsConstructor
public class TransportController {

    private final TransportService transportService;

    // POST /transports
    @PostMapping
    public ResponseEntity<TransportDetailResponse> requestTransport(@RequestBody TransportCreateRequest request) {
        TransportDetailResponse response = transportService.requestTransport(request);

        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    // PATCH /transports/{transport_id}/start
    @PatchMapping("/{transport_id}/start")
    public ResponseEntity<TransportSimpleResponse> startTransport(@PathVariable("transport_id") int transportId) {
        TransportSimpleResponse response = transportService.startTransport(transportId);

        return ResponseEntity.ok(response);
    }

    // PATCH /transports/{id}/complete
    @PatchMapping("/{transport_id}/complete")
    public ResponseEntity<TransportSimpleResponse> completeTransport(@PathVariable("transport_id") int transportId) {
        TransportSimpleResponse response = transportService.completeTransport(transportId);

        return ResponseEntity.ok(response);
    }

    // GET /transports/{transport_id}
    @GetMapping("/{transport_id}")
    public ResponseEntity<TransportDetailResponse> getTransport(@PathVariable("transport_id") int transportId) {
        TransportDetailResponse response = transportService.findTransportById(transportId);

        return ResponseEntity.ok(response);
    }

    // GET /transports
    @GetMapping
    public ResponseEntity<List<TransportSimpleResponse>> getAllTransports() {
        List<TransportSimpleResponse> response = transportService.findAllTransports();

        return ResponseEntity.ok(response);
    }

    // GET /transports/{transport_id}/valid-drugs
    @GetMapping("/{transport_id}/valid-drugs")
    public ResponseEntity<List<DrugResponse>> getValidDrugsForTransport(@PathVariable("transport_id") int transportId) {
        List<DrugResponse> response = transportService.findValidDrugsForTransport(transportId);

        return ResponseEntity.ok(response);
    }

    @GetMapping("/requested-drugs")
    public ResponseEntity<List<DrugResponse>> getRequestedDrugsForLatestTransport() {
        List<DrugResponse> response = transportService.findRequestedDrugsForLatestTransport();

        return ResponseEntity.ok(response);
    }
}
