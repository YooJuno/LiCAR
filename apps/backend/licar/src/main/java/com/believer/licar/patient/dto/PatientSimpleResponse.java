package com.believer.licar.patient.dto;

import com.believer.licar.patient.entity.Patient;
import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class PatientSimpleResponse {

    private final int patientID;
    private final String name;
    private final Integer roomNumber;

    public static PatientSimpleResponse from(Patient patient) {
        return PatientSimpleResponse.builder()
                .patientID(patient.getPatientId())
                .name(patient.getName())
                .roomNumber(patient.getRoomNumber())
                .build();
    }
}
