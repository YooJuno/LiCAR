package com.believer.licar.auth.service;

import com.believer.licar.auth.dto.NurseLoginRequest;
import com.believer.licar.auth.dto.PharmacistLoginRequest;
import com.believer.licar.global.exception.CustomException;
import com.believer.licar.global.exception.ErrorCode;
import com.believer.licar.user.entity.Nurse;
import com.believer.licar.user.entity.Pharmacist;
import com.believer.licar.user.repository.NurseRepository;
import com.believer.licar.user.repository.PharmacistRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class AuthService {

    private final NurseRepository nurseRepository;
    private final PharmacistRepository pharmacistRepository;

    public Nurse loginNurse(NurseLoginRequest request) {
        return nurseRepository.findByNurseIdAndName(request.getNurse_id(), request.getName())
                .orElseThrow(() -> new CustomException(ErrorCode.NURSE_AUTHENTICATION_FAILED));
    }

    public Pharmacist loginPharmacist(PharmacistLoginRequest request) {
        return pharmacistRepository.findByPharmacistIdAndName((request.getPharmacist_id()), request.getName())
                .orElseThrow(() -> new CustomException(ErrorCode.PHARMACIST_AUTHENTICATION_FAILED));
    }
}
