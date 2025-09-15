package com.believer.licar.prescription.controller;

import com.believer.licar.prescription.dto.*;
import com.believer.licar.prescription.entity.Drug;
import com.believer.licar.prescription.service.PrescriptionService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/api/v1/prescriptions")
@RequiredArgsConstructor
public class PrescriptionController {

    private final PrescriptionService prescriptionService;

    // POST /prescriptions/drugs
    @PostMapping("/drugs")
    public ResponseEntity<Drug> createDrug(@RequestBody DrugCreateRequest request) {
        Drug createDrug = prescriptionService.createDrug(request);

        return ResponseEntity.status(HttpStatus.CREATED).body(createDrug);
    }

    // POST /prescriptions
    @PostMapping
    public ResponseEntity<PrescriptionDetailResponse> createPrescription(@RequestBody PrescriptionCreateRequest request) {
        PrescriptionDetailResponse response = prescriptionService.createPrescription(request);

        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    // GET /prescriptions
    @GetMapping
    public ResponseEntity<List<PrescriptionSimpleResponse>> getPrescription(@RequestParam(required = false) Integer patient_id) {
        if (patient_id != null) {
            return ResponseEntity.ok(prescriptionService.findPrescriptionsByPatientId(patient_id));
        }

        return ResponseEntity.ok(prescriptionService.findAllPrescriptions());
    }

    // GET /prescriptions/{prescription_id}
    @GetMapping("/{prescription_id}")
    public ResponseEntity<PrescriptionDetailResponse> getPrescriptionDetail(@PathVariable("prescription_id") int prescriptionId) {
        return ResponseEntity.ok(prescriptionService.findPrescriptionById(prescriptionId));
    }

    // GET /prescriptions/valid?patient_id={patient_id}&date={yyyy-MM-dd}
    @GetMapping("/valid")
    public ResponseEntity<List<PrescriptionSimpleResponse>> getValidPrescriptions(
            @RequestParam("patient_id") int patientId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {

        List<PrescriptionSimpleResponse> response = prescriptionService.findValidPrescriptionsForPatient(patientId, date);
        return ResponseEntity.ok(response);
    }

    // GET /prescriptions/valid-drugs?patient_id={id}&date={yyyy-MM-dd}
    @GetMapping("/valid-drugs")
    public ResponseEntity<List<DrugResponse>> getValidDrugs(
            @RequestParam("patient_id") int patientId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {

        List<DrugResponse> response = prescriptionService.findValidDrugsForPatient(patientId, date);
        return ResponseEntity.ok(response);
    }
}
