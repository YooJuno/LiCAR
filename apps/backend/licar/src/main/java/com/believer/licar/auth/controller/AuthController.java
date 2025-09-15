package com.believer.licar.auth.controller;

import com.believer.licar.auth.dto.NurseLoginRequest;
import com.believer.licar.auth.dto.NurseLoginResponse;
import com.believer.licar.auth.dto.PharmacistLoginRequest;
import com.believer.licar.auth.dto.PharmacistLoginResponse;
import com.believer.licar.auth.service.AuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/nurse/login")
    public ResponseEntity<NurseLoginResponse> loginNurse(@RequestBody NurseLoginRequest request) {
        NurseLoginResponse response = authService.loginNurse(request);

        return ResponseEntity.ok(response);
    }

    @PostMapping("/pharmacist/login")
    public ResponseEntity<PharmacistLoginResponse> loginPharmacist(@RequestBody PharmacistLoginRequest request) {
        PharmacistLoginResponse response = authService.loginPharmacist(request);

        return ResponseEntity.ok(response);
    }
}
