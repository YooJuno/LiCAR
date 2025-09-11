package com.believer.licar.delivery.dto;

import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class DeliveryCreateRequest {

    private int nurseId;
    private int pharmacistId;
    private int patientId;
}
