package com.believer.licar.delivery.dto;

import com.believer.licar.delivery.entity.Delivery;
import com.believer.licar.delivery.enums.DeliveryStatus;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@Builder
public class DeliverySimpleResponse {

    private final int deliveryId;
    private final DeliveryStatus status;
    private final Integer robotId;
    private final String nurseName;

    public static DeliverySimpleResponse from(Delivery delivery) {
        return DeliverySimpleResponse.builder()
                .deliveryId(delivery.getDeliveryId())
                .status(delivery.getStatus())
                .robotId(delivery.getRobotId())
                .nurseName(delivery.getNurse().getName())
                .build();
    }
}
