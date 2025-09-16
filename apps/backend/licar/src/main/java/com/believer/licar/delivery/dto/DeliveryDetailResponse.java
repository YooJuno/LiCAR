package com.believer.licar.delivery.dto;

import com.believer.licar.delivery.entity.Delivery;
import com.believer.licar.delivery.enums.DeliveryStatus;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@Builder
public class DeliveryDetailResponse {

    private final int deliveryId;
    private final LocalDateTime requestTime;
    private final LocalDateTime sendTime;
    private final LocalDateTime successTime;
    private final DeliveryStatus status;
    private final Integer robotId;
    private final String nurseName;
    private final String pharmacistName;
    private final Integer patientId;

    public static DeliveryDetailResponse from(Delivery delivery)
    {
        return DeliveryDetailResponse.builder()
                .deliveryId(delivery.getDeliveryId())
                .requestTime(delivery.getRequestTime())
                .sendTime(delivery.getSendTime())
                .successTime(delivery.getSuccessTime())
                .status(delivery.getStatus())
                .robotId(delivery.getRobotId())
                .nurseName(delivery.getNurse().getName())
                .pharmacistName(delivery.getPharmacist().getName())
                .patientId(delivery.getPatient().getPatientId())
                .build();
    }
}
