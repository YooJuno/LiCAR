package com.believer.licar.delivery.dto;

import com.believer.licar.delivery.entity.Delivery;
import com.believer.licar.delivery.enums.DeliveryStatus;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@Builder
public class DeliveryResponse {

    private final int deliveryId;
    private final LocalDateTime requestTime;
    private final LocalDateTime sendTime;
    private final LocalDateTime successTime;
    private final DeliveryStatus status;
    private final String nurseName;
    private final String pharmacistName;
    private final String patientName;

    public static DeliveryResponse from(Delivery delivery) {
        return DeliveryResponse.builder()
                .deliveryId(delivery.getDeliveryId())
                .requestTime(delivery.getRequestTime())
                .sendTime(delivery.getSendTime())
                .successTime(delivery.getSuccessTime())
                .status(delivery.getStatus())
                .nurseName(delivery.getNurse().getName())
                .pharmacistName(delivery.getPharmacist().getName())
                .patientName(delivery.getPatient().getName())
                .build();

    }
}
