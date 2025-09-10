package com.believer.licar.patient.dto;

import com.believer.licar.patient.entity.Patient;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDate;

@Getter
@Builder
public class PatientResponse {

    private final int patientId;
    private final String name;
    private final LocalDate birthday;
    private final LocalDate admissionDate;
    private final Integer roomNumber;
    private final String nurseName;

    public static PatientResponse from(Patient patient) {
        return PatientResponse.builder()
                .patientId(patient.getPatientId())
                .name(patient.getName())
                .birthday(patient.getBirthday())
                .admissionDate(patient.getAdmissionDate())
                .roomNumber(patient.getRoomNumber())
                .nurseName(patient.getNurse().getName())
                .build();
    }
}
