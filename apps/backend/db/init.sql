-- ENUM 타입 정의
CREATE TYPE delivery_status AS ENUM ('requested', 'in_transit', 'completed');

-- 간호사 테이블
CREATE TABLE "Nurse" (
    "nurse_id" SERIAL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL,
    "department" VARCHAR(50)
);

-- 약사 테이블
CREATE TABLE "Pharmacist" (
    "pharmacist_id" SERIAL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL
);

-- 환자 테이블
CREATE TABLE "Patient" (
    "patient_id" SERIAL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL,
    "birthday" DATE,
    "admission_date" DATE,
    "discharge_date" DATE,
    "room_number" INTEGER,
    "nurse_id" INTEGER NOT NULL,
    FOREIGN KEY ("nurse_id") REFERENCES "Nurse" ("nurse_id")
);

-- 운송 정보 테이블
CREATE TABLE "Delivery" (
    "delivery_id" SERIAL PRIMARY KEY,
    "request_time" TIMESTAMP,
    "send_time" TIMESTAMP,
    "success_time" TIMESTAMP,
    "status" delivery_status DEFAULT 'requested',
    "nurse_id" INTEGER NOT NULL,
    "pharmacist_id" INTEGER NOT NULL,
    "patient_id" INTEGER NOT NULL,
    CHECK (
        (request_time IS NULL OR send_time IS NULL OR success_time IS NULL)
        OR (request_time <= send_time AND send_time <= success_time)
    ),
    FOREIGN KEY ("nurse_id") REFERENCES "Nurse" ("nurse_id"),
    FOREIGN KEY ("pharmacist_id") REFERENCES "Pharmacist" ("pharmacist_id"),
    FOREIGN KEY ("patient_id") REFERENCES "Patient" ("patient_id")
);

-- 처방전 테이블
CREATE TABLE "Prescription" (
    "prescription_id" SERIAL PRIMARY KEY,
    "date" DATE,
    "period" INTEGER,
    "explain" VARCHAR(300),
    "patient_id" INTEGER NOT NULL,
    CHECK (period > 0),
    FOREIGN KEY ("patient_id") REFERENCES "Patient" ("patient_id")
);

-- 약 정보 테이블
CREATE TABLE "Drug" (
    "drug_id" SERIAL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL,
    "form" VARCHAR(20),
    "dosage" INTEGER,
    "unit" VARCHAR(20)
);

-- 처방전_약 정보 테이블
CREATE TABLE "Prescription_Drug" (
    "prescription_id" INTEGER NOT NULL,
    "drug_id" INTEGER NOT NULL,
    PRIMARY KEY ("prescription_id", "drug_id"),
    FOREIGN KEY ("prescription_id") REFERENCES "Prescription" ("prescription_id"),
    FOREIGN KEY ("drug_id") REFERENCES "Drug" ("drug_id")
);