package com.believer.licar.delivery.service;

import com.believer.licar.delivery.dto.DeliveryCreateRequest;
import com.believer.licar.delivery.dto.DeliveryDetailResponse;
import com.believer.licar.delivery.dto.DeliverySimpleResponse;
import com.believer.licar.delivery.entity.Delivery;
import com.believer.licar.delivery.enums.DeliveryStatus;
import com.believer.licar.delivery.repository.DeliveryRepository;
import com.believer.licar.global.exception.CustomException;
import com.believer.licar.global.exception.ErrorCode;
import com.believer.licar.notification.dto.NotificationCompleteResponse;
import com.believer.licar.notification.dto.NotificationRequestResponse;
import com.believer.licar.notification.service.NotificationService;
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
    private final NotificationService notificationService;
    private final NurseRepository nurseRepository;
    private final PharmacistRepository pharmacistRepository;
    private final PrescriptionService prescriptionService;

    @Transactional
    public DeliveryDetailResponse requestDelivery(DeliveryCreateRequest request) {
        Patient patient = patientRepository.findById(request.getPatientId())
                .orElseThrow(() -> new CustomException(ErrorCode.PATIENT_NOT_FOUND));
        Nurse nurse = nurseRepository.findById(request.getNurseId())
                .orElseThrow(() -> new CustomException(ErrorCode.NURSE_NOT_FOUND));
        Pharmacist pharmacist = pharmacistRepository.findById(request.getPharmacistId())
                .orElseThrow(() -> new CustomException(ErrorCode.PHARMACIST_NOT_FOUND));

        Delivery delivery = new Delivery(request.getRobotId(), nurse, pharmacist, patient);
        Delivery savedDelivery = deliveryRepository.save(delivery);

        // SSE
        NotificationRequestResponse notification = NotificationRequestResponse.from(savedDelivery);
        notificationService.sendToPharmacist(savedDelivery.getPharmacist().getPharmacistId(), notification);

        return DeliveryDetailResponse.from(savedDelivery);
    }

    @Transactional
    public DeliverySimpleResponse startDelivery(int deliveryId) {
        Delivery delivery = findDeliveryEntityById(deliveryId);

        if (delivery.getStatus() != DeliveryStatus.requested) {
            throw new CustomException(ErrorCode.INVALID_INPUT_VALUE);
        }
        delivery.startTransit();

        return DeliverySimpleResponse.from(delivery);
    }

    @Transactional
    public DeliverySimpleResponse completeDelivery(int deliveryId) {
        Delivery delivery = findDeliveryEntityById(deliveryId);

        if (delivery.getStatus() != DeliveryStatus.in_transit) {
            throw new CustomException(ErrorCode.INVALID_INPUT_VALUE);
        }
        delivery.completeDelivery();

        // SSE
        NotificationCompleteResponse notification = NotificationCompleteResponse.from(delivery);
        notificationService.setToNurse(delivery.getNurse().getNurseId(), notification);

        return DeliverySimpleResponse.from(delivery);
    }

    @Transactional(readOnly = true)
    public DeliveryDetailResponse findDeliveryById(int deliveryId) {

        return DeliveryDetailResponse.from(findDeliveryEntityById(deliveryId));
    }

    @Transactional(readOnly = true)
    public List<DeliverySimpleResponse> findAllDeliveries() {
        return deliveryRepository.findAll().stream()
                .map(DeliverySimpleResponse::from)
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
    public List<DrugResponse> findValidDrugsForDelivery(int deliveryId) {
        Delivery delivery = findDeliveryEntityById(deliveryId);
        int patientId = delivery.getPatient().getPatientId();
        LocalDate requestDate = delivery.getRequestTime().toLocalDate();

        return prescriptionService.findValidDrugsForPatient(deliveryId, LocalDate.now());
    }

    private Delivery findDeliveryEntityById(int deliveryId) {
        return deliveryRepository.findById(deliveryId)
                .orElseThrow(() -> new CustomException(ErrorCode.DELIVERY_NOT_FOUND));
    }

    @Transactional(readOnly = true)
    public List<DrugResponse> findRequestedDrugsForLatestDelivery() {
        Delivery latestDelivery = deliveryRepository.findFirstByOrderByDeliveryIdDesc()
                .orElseThrow(() -> new CustomException(ErrorCode.DELIVERY_NOT_FOUND));

        if (latestDelivery.getStatus() != DeliveryStatus.requested) {
            throw new CustomException(ErrorCode.DELIVERY_NOT_FOUND);
        }

        int patientId = latestDelivery.getPatient().getPatientId();

        return prescriptionService.findValidDrugsForPatient(patientId, LocalDate.now());
    }
}
