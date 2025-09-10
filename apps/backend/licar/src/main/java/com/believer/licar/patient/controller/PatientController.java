package com.believer.licar.patient.controller;

import com.believer.licar.patient.dto.PatientResponse;
import com.believer.licar.patient.dto.PatientSearchResponse;
import com.believer.licar.patient.service.PatientService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/patients")
@RequiredArgsConstructor
public class PatientController {

    private final PatientService patientService;

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
