package com.believer.licar.patient.dto;

import com.believer.licar.patient.entity.Patient;
import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class PatientSearchResponse {

    private final int patientID;
    private final String name;
    private final Integer roomNumber;

    public static PatientSearchResponse from(Patient patient) {
        return PatientSearchResponse.builder()
                .patientID(patient.getPatientId())
                .name(patient.getName())
                .roomNumber(patient.getPatientId())
                .build();
    }
}
