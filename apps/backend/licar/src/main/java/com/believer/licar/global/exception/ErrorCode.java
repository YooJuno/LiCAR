package com.believer.licar.global.exception;

import lombok.Getter;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;

@Getter
@RequiredArgsConstructor
public enum ErrorCode {

    // 400 Bad Request
    INVALID_INPUT_VALUE(HttpStatus.BAD_REQUEST, "E001", "입력 값이 올바르지 않습니다."),

    // 401 Unauthorized
    NURSE_AUTHENTICATION_FAILED(HttpStatus.UNAUTHORIZED, "E002", "간호사 인증에 실패했습니다."),
    PHARMACIST_AUTHENTICATION_FAILED(HttpStatus.UNAUTHORIZED, "E003", "약사 인증에 실패했습니다."),

    // 404 Not Found
    PATIENT_NOT_FOUND(HttpStatus.NOT_FOUND, "E004", "해당 환자를 찾을 수 없습니다."),
    PRESCRIPTION_NOT_FOUND(HttpStatus.NOT_FOUND, "E005", "해당 처방전을 찾을 수 없습니다."),

    // 500 Internal Server Error
    INTERNAL_SERVER_ERROR(HttpStatus.INTERNAL_SERVER_ERROR, "E999", "서버 내부 오류가 발생했습니다.");

    private final HttpStatus status;
    private final String code;
    private final String message;
}
