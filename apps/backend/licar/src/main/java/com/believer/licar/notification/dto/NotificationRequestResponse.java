package com.believer.licar.notification.dto;

import com.believer.licar.delivery.entity.Delivery;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@Builder
public class NotificationRequestResponse {

    private final int deliveryId;
    private final LocalDateTime requestTime;
    private final int nurseId;
    private final int pharmacistId;

    public static NotificationRequestResponse from(Delivery delivery) {
        return NotificationRequestResponse.builder()
                .deliveryId(delivery.getDeliveryId())
                .requestTime(delivery.getRequestTime())
                .nurseId(delivery.getNurse().getNurseId())
                .pharmacistId(delivery.getPharmacist().getPharmacistId())
                .build();
    }
}
