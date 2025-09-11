package com.believer.licar.patient.controller;

import com.believer.licar.patient.dto.PatientCreateRequest;
import com.believer.licar.patient.dto.PatientResponse;
import com.believer.licar.patient.dto.PatientSearchResponse;
import com.believer.licar.patient.service.PatientService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("api/v1/patients")
@RequiredArgsConstructor
public class PatientController {

    private final PatientService patientService;

    // POST /patients
    @PostMapping
    public ResponseEntity<PatientResponse> createPatient(@RequestBody PatientCreateRequest request) {
        PatientResponse createdPatient = patientService.createPatient(request);

        return ResponseEntity.status(HttpStatus.CREATED).body(createdPatient);
    }

    // GET /patients
    @GetMapping
    public ResponseEntity<List<PatientResponse>> getAllPatients() {
        List<PatientResponse> patients = patientService.findAllPatients();

        return ResponseEntity.ok(patients);
    }

    // GET /patients?name={name}
    @GetMapping(params = "name")
    public ResponseEntity<List<PatientSearchResponse>> searchPatientsByName(@RequestParam String name) {
        List<PatientSearchResponse> patients = patientService.searchPatientsByName(name);

        return ResponseEntity.ok(patients);
    }
}
