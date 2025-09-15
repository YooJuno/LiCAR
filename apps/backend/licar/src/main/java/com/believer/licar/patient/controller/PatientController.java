package com.believer.licar.patient.controller;

import com.believer.licar.patient.dto.PatientCreateRequest;
import com.believer.licar.patient.dto.PatientDetailResponse;
import com.believer.licar.patient.dto.PatientSimpleResponse;
import com.believer.licar.patient.service.PatientService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/patients")
@RequiredArgsConstructor
public class PatientController {

    private final PatientService patientService;

    // POST /api/v1/patients
    @PostMapping
    public ResponseEntity<PatientSimpleResponse> createPatient(@RequestBody PatientCreateRequest request) {
        PatientSimpleResponse createdPatient = patientService.createPatient(request);

        return ResponseEntity.status(HttpStatus.CREATED).body(createdPatient);
    }

    // GET /api/v1/patients
    @GetMapping
    public ResponseEntity<List<PatientSimpleResponse>> getAllPatients() {
        List<PatientSimpleResponse> patients = patientService.findAllPatients();

        return ResponseEntity.ok(patients);
    }

    // GET /api/v1/patients?name={name}
    @GetMapping(params = "name")
    public ResponseEntity<List<PatientSimpleResponse>> searchPatientsByName(@RequestParam String name) {
        List<PatientSimpleResponse> patients = patientService.searchPatientsByName(name);

        return ResponseEntity.ok(patients);
    }

    // GET /api/v1/patients/{id}
    @GetMapping("/{id}")
    public ResponseEntity<PatientDetailResponse> getPatientDetail(@PathVariable int id ) {
        PatientDetailResponse patient = patientService.findPatientById(id);

        return ResponseEntity.ok(patient);
    }
}
