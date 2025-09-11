package com.believer.licar.delivery.controller;

import com.believer.licar.delivery.dto.DeliveryCreateRequest;
import com.believer.licar.delivery.dto.DeliveryResponse;
import com.believer.licar.delivery.service.DeliveryService;
import com.believer.licar.prescription.dto.DrugResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/deliveries")
@RequiredArgsConstructor
public class DeliveryController {

    private final DeliveryService deliveryService;

    // POST /deliveries
    @PostMapping
    public ResponseEntity<DeliveryResponse> requestDelivery(@RequestBody DeliveryCreateRequest request) {
        DeliveryResponse response = deliveryService.requestDelivery(request);

        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    // PATCH /deliveries/{delivery_id}/start
    @PatchMapping("/{delivery_id}/start")
    public ResponseEntity<DeliveryResponse> startDelivery(@PathVariable("delivery_id") int deliveryId) {
        DeliveryResponse response = deliveryService.startDelivery(deliveryId);

        return ResponseEntity.ok(response);
    }

    // GET /deliveries/{id}/complete
    @PatchMapping("/{delivery_id}/complete")
    public ResponseEntity<DeliveryResponse> completeDelivery(@PathVariable("delivery_id") int deliveryId) {
        DeliveryResponse response = deliveryService.completeDelivery(deliveryId);

        return ResponseEntity.ok(response);
    }

    // GET /deliveries/{delivery_id}
    @GetMapping("/{delivery_id}")
    public ResponseEntity<DeliveryResponse> getDelivery(@PathVariable("delivery_id") int deliveryId) {
        DeliveryResponse response = deliveryService.findDeliveryById(deliveryId);

        return ResponseEntity.ok(response);
    }

    // GET /deliveries
    @GetMapping
    public ResponseEntity<List<DeliveryResponse>> getAllDeliveries() {
        List<DeliveryResponse> response = deliveryService.findAllDeliveries();

        return ResponseEntity.ok(response);
    }

    // GET /deliveries/valid-drugs?=patient_id
    @GetMapping("/valid-drugs")
    public ResponseEntity<List<DrugResponse>> getValidDrugsForDelivery(@RequestParam("patient_id") int patientId) {
        List<DrugResponse> response = deliveryService.findValidDrugsForDelivery(patientId);

        return ResponseEntity.ok(response);
    }

    // GET /deliveries/{delivery_id}/valid-drugs
    @GetMapping("/{delivery_id}/valid-drugs")
    public ResponseEntity<List<DrugResponse>> getValidDrugsForDeliveryRequest(@PathVariable("delivery_id") int deliveryId) {
        List<DrugResponse> response = deliveryService.findValidDrugsForDeliveryRequest(deliveryId);

        return ResponseEntity.ok(response);
    }
}
