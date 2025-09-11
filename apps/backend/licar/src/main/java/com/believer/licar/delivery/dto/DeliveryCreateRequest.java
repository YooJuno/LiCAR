package com.believer.licar.delivery.dto;

import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class DeliveryCreateRequest {

    private Integer robotId;
    private int nurseId;
    private int pharmacistId;
    private int patientId;
}
