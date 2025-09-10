package com.believer.licar.patient.service;

import com.believer.licar.global.exception.CustomException;
import com.believer.licar.global.exception.ErrorCode;
import com.believer.licar.patient.dto.PatientCreateRequest;
import com.believer.licar.patient.dto.PatientResponse;
import com.believer.licar.patient.dto.PatientSearchResponse;
import com.believer.licar.patient.entity.Patient;
import com.believer.licar.patient.repository.PatientRepository;
import com.believer.licar.user.entity.Nurse;
import com.believer.licar.user.repository.NurseRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class PatientService {

    private final PatientRepository patientRepository;
    private final NurseRepository nurseRepository;

    @Transactional
    public PatientResponse createPatient(PatientCreateRequest request) {
        Nurse nurse = nurseRepository.findById(request.getNurseId())
                .orElseThrow(() -> new CustomException(ErrorCode.NURSE_NOT_FOUND));

        Patient newPatient = request.toEntity(nurse);

        Patient savedPatient = patientRepository.save(newPatient);

        return PatientResponse.from(savedPatient);
    }

    @Transactional(readOnly = true)
    public List<PatientResponse> findAllPatients() {
        return patientRepository.findAll().stream()
                .map(PatientResponse::from)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<PatientSearchResponse> searchPatientsByName(String name) {
        return patientRepository.findByNameContaining(name).stream()
                .map(PatientSearchResponse::from)
                .collect(Collectors.toList());
    }
}
