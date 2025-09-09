package com.believer.licar.patient.entity;

import com.believer.licar.user.entity.Nurse;

import java.time.LocalDate;

public class Patient {

    private int patientId;

    private String name;

    private LocalDate birthday;

    private LocalDate admissionDate;

    private LocalDate dischargeDate;

    private Integer roomNumber;

    private Nurse nurse;
}
