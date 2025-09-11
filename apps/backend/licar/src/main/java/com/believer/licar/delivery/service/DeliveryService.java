package com.believer.licar.delivery.service;

import com.believer.licar.delivery.dto.DeliveryCreateRequest;
import com.believer.licar.delivery.dto.DeliveryResponse;
import com.believer.licar.delivery.entity.Delivery;
import com.believer.licar.delivery.repository.DeliveryRepository;
import com.believer.licar.global.exception.CustomException;
import com.believer.licar.global.exception.ErrorCode;
import com.believer.licar.patient.entity.Patient;
import com.believer.licar.patient.repository.PatientRepository;
import com.believer.licar.prescription.dto.DrugResponse;
import com.believer.licar.prescription.service.PrescriptionService;
import com.believer.licar.user.entity.Nurse;
import com.believer.licar.user.entity.Pharmacist;
import com.believer.licar.user.repository.NurseRepository;
import com.believer.licar.user.repository.PharmacistRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class DeliveryService {

    private final DeliveryRepository deliveryRepository;
    private final PatientRepository patientRepository;
    private final NurseRepository nurseRepository;
    private final PharmacistRepository pharmacistRepository;
    private final PrescriptionService prescriptionService;

    @Transactional
    public DeliveryResponse requestDelivery(DeliveryCreateRequest request) {
        Patient patient = patientRepository.findById(request.getPatientId())
                .orElseThrow(() -> new CustomException(ErrorCode.PATIENT_NOT_FOUND));
        Nurse nurse = nurseRepository.findById(request.getNurseId())
                .orElseThrow(() -> new CustomException(ErrorCode.NURSE_NOT_FOUND));
        Pharmacist pharmacist = pharmacistRepository.findById(request.getPharmacistId())
                .orElseThrow(() -> new CustomException(ErrorCode.PHARMACIST_NOT_FOUND));

        Delivery delivery = new Delivery(nurse, pharmacist, patient);
        Delivery savedDelivery = deliveryRepository.save(delivery);

        // SSE

        return DeliveryResponse.from(savedDelivery);
    }

    @Transactional
    public DeliveryResponse startDelivery(int deliveryId) {
        Delivery delivery = findDeliveryEntityById(deliveryId);
        delivery.startTransit();
        return DeliveryResponse.from(delivery);
    }

    @Transactional
    public DeliveryResponse completeDelivery(int deliveryId) {
        Delivery delivery = findDeliveryEntityById(deliveryId);
        delivery.completeDelivery();
        return DeliveryResponse.from(delivery);
    }

    @Transactional(readOnly = true)
    public DeliveryResponse findDeliveryById(int deliveryId) {
        return DeliveryResponse.from(findDeliveryEntityById(deliveryId));
    }

    @Transactional(readOnly = true)
    public List<DeliveryResponse> findAllDeliveries() {
        return deliveryRepository.findAll().stream()
                .map(DeliveryResponse::from)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<DrugResponse> findValidDrugsForDeliveryRequest(int deliveryId) {
        Delivery delivery = findDeliveryEntityById(deliveryId);
        Patient patient = delivery.getPatient();
        LocalDate requestDate = delivery.getRequestTime().toLocalDate();

        return prescriptionService.findValidDrugsForPatient(patient.getPatientId(), requestDate);
    }

    @Transactional(readOnly = true)
    public List<DrugResponse> findValidDrugsForDelivery(int patientId) {
        return prescriptionService.findValidDrugsForPatient(patientId, LocalDate.now());
    }

    private Delivery findDeliveryEntityById(int deliveryId) {
        return deliveryRepository.findById(deliveryId)
                .orElseThrow(() -> new CustomException(ErrorCode.DELIVERY_NOT_FOUND));
    }
}
