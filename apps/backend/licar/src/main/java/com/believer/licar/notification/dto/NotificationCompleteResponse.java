package com.believer.licar.notification.dto;

import com.believer.licar.delivery.entity.Delivery;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@Builder
public class NotificationCompleteResponse {

    private final int deliveryId;
    private final LocalDateTime successTime;
    private final int nurseId;
    private final int pharmacistId;

    public static NotificationCompleteResponse from(Delivery delivery) {
        return NotificationCompleteResponse.builder()
                .deliveryId(delivery.getDeliveryId())
                .successTime(delivery.getSuccessTime())
                .nurseId(delivery.getNurse().getNurseId())
                .pharmacistId(delivery.getPharmacist().getPharmacistId())
                .build();
    }
}
