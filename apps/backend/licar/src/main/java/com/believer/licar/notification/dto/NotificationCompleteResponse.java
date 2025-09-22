package com.believer.licar.notification.dto;

import com.believer.licar.transport.entity.Transport;
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

    public static NotificationCompleteResponse from(Transport delivery) {
        return NotificationCompleteResponse.builder()
                .deliveryId(delivery.getTransportId())
                .successTime(delivery.getArrivedTime())
                .nurseId(delivery.getNurse().getNurseId())
                .pharmacistId(delivery.getPharmacist().getPharmacistId())
                .build();
    }
}
