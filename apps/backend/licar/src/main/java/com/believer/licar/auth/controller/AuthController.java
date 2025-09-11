package com.believer.licar.auth.controller;

import com.believer.licar.auth.dto.NurseLoginRequest;
import com.believer.licar.auth.dto.PharmacistLoginRequest;
import com.believer.licar.auth.service.AuthService;
import com.believer.licar.user.entity.Nurse;
import com.believer.licar.user.entity.Pharmacist;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("api/v1/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/nurse/login")
    public ResponseEntity<String> loginNurse(@RequestBody NurseLoginRequest request) {
        Nurse nurse = authService.loginNurse(request);

        return ResponseEntity.ok(nurse.getName());
    }

    @PostMapping("pharmacist/login")
    public ResponseEntity<String> loginPharmacist(@RequestBody PharmacistLoginRequest request) {
        Pharmacist pharmacist = authService.loginPharmacist(request);

        return ResponseEntity.ok(pharmacist.getName());
    }
}
