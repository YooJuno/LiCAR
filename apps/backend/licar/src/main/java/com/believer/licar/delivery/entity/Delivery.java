package com.believer.licar.delivery.entity;

import com.believer.licar.delivery.enums.DeliveryStatus;
import com.believer.licar.patient.entity.Patient;
import com.believer.licar.user.entity.Nurse;
import com.believer.licar.user.entity.Pharmacist;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;

@Entity
@Table(name = "deliveries")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Delivery {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "delivery_id")
    private int deliveryId;

    @Column(name = "request_time")
    private LocalDateTime requestTime;

    @Column(name = "send_time")
    private LocalDateTime sendTime;

    @Column(name = "success_time")
    private LocalDateTime successTime;

    @JdbcTypeCode(SqlTypes.NAMED_ENUM)
    @Column(name = "status", columnDefinition = "delivery_status")
    private DeliveryStatus status;

    @Column(name = "robot_id", nullable = false)
    private Integer robotId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "nurse_id", nullable = false)
    private Nurse nurse;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "pharmacist_id", nullable = false)
    private Pharmacist pharmacist;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "patient_id", nullable = false)
    private Patient patient;

    @PrePersist
    protected void onCreate() {
        this.requestTime = LocalDateTime.now();
        this.status = DeliveryStatus.requested;
    }

    public Delivery(Integer robotId, Nurse nurse, Pharmacist pharmacist, Patient patient) {
        this.robotId = robotId;
        this.nurse = nurse;
        this.pharmacist = pharmacist;
        this.patient = patient;
    }

    public void startTransit() {
        this.status = DeliveryStatus.in_transit;
        this.sendTime = LocalDateTime.now();
    }

    public void completeDelivery() {
        this.status = DeliveryStatus.completed;
        this.successTime = LocalDateTime.now();
    }
}
