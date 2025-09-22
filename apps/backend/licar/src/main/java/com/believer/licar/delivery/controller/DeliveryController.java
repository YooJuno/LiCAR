package com.believer.licar.delivery.controller;

import com.believer.licar.delivery.dto.DeliveryCreateRequest;
import com.believer.licar.delivery.dto.DeliveryDetailResponse;
import com.believer.licar.delivery.dto.DeliverySimpleResponse;
import com.believer.licar.delivery.service.DeliveryService;
import com.believer.licar.prescription.dto.DrugResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/deliveries")
@RequiredArgsConstructor
public class DeliveryController {

    private final DeliveryService deliveryService;

    // POST /deliveries
    @PostMapping
    public ResponseEntity<DeliveryDetailResponse> requestDelivery(@RequestBody DeliveryCreateRequest request) {
        DeliveryDetailResponse response = deliveryService.requestDelivery(request);

        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    // PATCH /deliveries/{delivery_id}/start
    @PatchMapping("/{delivery_id}/start")
    public ResponseEntity<DeliverySimpleResponse> startDelivery(@PathVariable("delivery_id") int deliveryId) {
        DeliverySimpleResponse response = deliveryService.startDelivery(deliveryId);

        return ResponseEntity.ok(response);
    }

    // PATCH /deliveries/{id}/complete
    @PatchMapping("/{delivery_id}/complete")
    public ResponseEntity<DeliverySimpleResponse> completeDelivery(@PathVariable("delivery_id") int deliveryId) {
        DeliverySimpleResponse response = deliveryService.completeDelivery(deliveryId);

        return ResponseEntity.ok(response);
    }

    // GET /deliveries/{delivery_id}
    @GetMapping("/{delivery_id}")
    public ResponseEntity<DeliveryDetailResponse> getDelivery(@PathVariable("delivery_id") int deliveryId) {
        DeliveryDetailResponse response = deliveryService.findDeliveryById(deliveryId);

        return ResponseEntity.ok(response);
    }

    // GET /deliveries
    @GetMapping
    public ResponseEntity<List<DeliverySimpleResponse>> getAllDeliveries() {
        List<DeliverySimpleResponse> response = deliveryService.findAllDeliveries();

        return ResponseEntity.ok(response);
    }

    // GET /deliveries/{delivery_id}/valid-drugs
    @GetMapping("/{delivery_id}/valid-drugs")
    public ResponseEntity<List<DrugResponse>> getValidDrugsForDelivery(@PathVariable("delivery_id") int deliveryId) {
        List<DrugResponse> response = deliveryService.findValidDrugsForDelivery(deliveryId);

        return ResponseEntity.ok(response);
    }

    @GetMapping("/requested-drugs")
    public ResponseEntity<List<DrugResponse>> getRequestedDrugsForLatestDelivery() {
        List<DrugResponse> response = deliveryService.findRequestedDrugsForLatestDelivery();

        return ResponseEntity.ok(response);
    }
}
