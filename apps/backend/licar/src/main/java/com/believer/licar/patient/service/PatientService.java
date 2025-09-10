package com.believer.licar.patient.service;

import com.believer.licar.patient.dto.PatientResponse;
import com.believer.licar.patient.dto.PatientSearchResponse;
import com.believer.licar.patient.repository.PatientRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class PatientService {

    private final PatientRepository patientRepository;

    public List<PatientResponse> findAllPatients() {
        return patientRepository.findAll().stream()
                .map(PatientResponse::from)
                .collect(Collectors.toList());
    }

    public List<PatientSearchResponse> searchPatientsByName(String name) {
        return patientRepository.findByNameContaining(name).stream()
                .map(PatientSearchResponse::from)
                .collect(Collectors.toList());
    }
}
