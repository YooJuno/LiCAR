import cv2
import yaml
import time
import threading
from typing import List, Dict

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from ultralytics import YOLO

# --- 라즈베리 파이 하드웨어 제어 (시뮬레이션) ---
# 실제 라즈베리 파이에서는 이 부분을 RPi.GPIO와 lgpio 코드로 교체하세요.
class HardwareController:
    def __init__(self):
        self.is_pi = False
        try:
            import RPi.GPIO as GPIO
            import lgpio
            self.GPIO = GPIO
            self.lgpio = lgpio
            
            # LED 설정
            self.CHIP = 0
            self.LED_GREEN_PIN = 20
            self.h = self.lgpio.gpiochip_open(self.CHIP)
            self.lgpio.gpio_claim_output(self.h, 0, self.LED_GREEN_PIN, 0)
            
            print("하드웨어 컨트롤러: 라즈베리 파이 환경에서 실행됩니다.")
            self.is_pi = True
        except (ImportError, RuntimeError):
            print("하드웨어 컨트롤러: 라즈베리 파이가 아닌 환경입니다. LED 제어를 시뮬레이션합니다.")

    def green_led_on(self):
        if self.is_pi:
            self.lgpio.gpio_write(self.h, self.LED_GREEN_PIN, 1)
        print("[LED] 초록색 LED ON")

    def green_led_off(self):
        if self.is_pi:
            self.lgpio.gpio_write(self.h, self.LED_GREEN_PIN, 0)
        print("[LED] 초록색 LED OFF")

    def cleanup(self):
        if self.is_pi:
            self.lgpio.gpio_write(self.h, self.LED_GREEN_PIN, 0)
            self.lgpio.gpiochip_close(self.h)
        print("하드웨어 리소스 정리 완료.")


# --- 상태 관리 (Thread-safe) ---
class DetectionStateManager:
    def __init__(self):
        self.detection_list: Dict[str, bool] = {}
        self.is_active = False
        self.lock = threading.Lock()

    def start_detection_session(self, pills: List[str]):
        with self.lock:
            self.detection_list = {pill: False for pill in pills}
            self.is_active = True
            print(f"새로운 검증 세션 시작. 목표: {list(self.detection_list.keys())}")

    def stop_detection_session(self):
        with self.lock:
            self.is_active = False
            self.detection_list = {}
            print("검증 세션 중지.")

    def mark_pill_as_found(self, pill_name: str):
        with self.lock:
            if pill_name in self.detection_list and not self.detection_list[pill_name]:
                self.detection_list[pill_name] = True
                print(f"** 약품 '{pill_name}' 발견! **")

    def are_all_pills_found(self) -> bool:
        with self.lock:
            if not self.is_active or not self.detection_list:
                return False
            return all(self.detection_list.values())

# --- 전역 객체 ---
# 설정
MODEL_PATH = '/home/ssafy/git/S13P21C206/apps/raspberrypi/ros2_ws/src/rc522_pkg/rc522_pkg/best.pt' # 실제 best.pt 경로로 수정
DATA_YAML_PATH = '/home/ssafy/git/S13P21C206/apps/raspberrypi/ros2_ws/src/rc522_pkg/rc522_pkg/data.yaml' # 실제 data.yaml 경로로 수정
CONFIDENCE_THRESHOLD = 0.65

# 객체 인스턴스화
app = FastAPI()
state_manager = DetectionStateManager()
hardware = HardwareController()

# --- 모델 및 클래스 이름 로드 ---
try:
    model = YOLO(MODEL_PATH)
    # with open(DATA_YAML_PATH, 'r', encoding='utf-8') as f:
    #     data = yaml.safe_load(f)
    # CLASS_NAMES = data['names']
    # YOLO 모델 객체에서 직접 클래스 이름 가져오기
    CLASS_NAMES = model.names
    print("AI 모델 로드 성공.")
except Exception as e:
    print(f"초기화 오류: {e}")
    exit()

# --- 백그라운드 영상 처리 스레드 ---
def video_detection_thread():
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("오류: USB 카메라를 열 수 없습니다.")
        return

    print("영상 처리 스레드 시작. API 요청 대기 중...")
    while True:
        # 1. 현재 검증 세션이 활성화 상태인지 확인
        if not state_manager.is_active:
            time.sleep(0.5) # 비활성 시 CPU 사용량 줄이기
            continue

        # 2. 카메라에서 프레임 읽기
        ret, frame = cap.read()
        if not ret:
            print("프레임 읽기 실패")
            time.sleep(1)
            continue
            
        # 3. YOLO 모델로 객체 탐지
        results = model(frame, verbose=False, conf=CONFIDENCE_THRESHOLD)

        # 4. 탐지된 객체 처리
        for r in results:
            for box in r.boxes:
                class_id = int(box.cls[0])
                pill_name = CLASS_NAMES[class_id]
                
                # 상태 관리자를 통해 해당 약품을 찾았다고 표시
                state_manager.mark_pill_as_found(pill_name)

        # 5. 모든 약품을 찾았는지 확인
        if state_manager.are_all_pills_found():
            hardware.green_led_on()
            print("목표 달성! 모든 약품을 찾았습니다.")
            # 성공 후 세션 자동 종료
            state_manager.stop_detection_session()

        # (디버깅용) 화면에 영상 표시. 실제 운영 시에는 주석 처리
        # cv2.imshow("Detection", results[0].plot())
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    cap.release()
    cv2.destroyAllWindows()


# --- FastAPI 엔드포인트 ---
class DetectionRequest(BaseModel):
    pills: List[str]

@app.post("/start-detection")
def start_detection(request: DetectionRequest):
    """실시간 약품 검증 세션을 시작합니다."""
    if not request.pills:
        return {"status": "error", "message": "약품 목록이 비어있습니다."}
    
    # LED 초기화
    hardware.green_led_off()
    # 새로운 목표 약품 목록으로 상태 관리자 설정
    state_manager.start_detection_session(request.pills)
    
    return {"status": "success", "message": f"Detection started for: {request.pills}"}

@app.post("/stop-detection")
def stop_detection():
    """진행 중인 검증 세션을 중지합니다."""
    hardware.green_led_off()
    state_manager.stop_detection_session()
    return {"status": "success", "message": "Detection stopped."}

@app.get("/status")
def get_status():
    """현재 검증 상태를 반환합니다."""
    with state_manager.lock:
        return {
            "is_active": state_manager.is_active,
            "detection_list": state_manager.detection_list
        }

# --- 메인 실행 ---
if __name__ == "__main__":
    try:
        # 백그라운드에서 영상 처리 스레드 시작
        detection_thread = threading.Thread(target=video_detection_thread, daemon=True)
        detection_thread.start()
        
        # 메인 스레드에서 FastAPI 서버 실행
        uvicorn.run(app, host="0.0.0.0", port=8080)
    finally:
        # 프로그램 종료 시 하드웨어 리소스 정리
        hardware.cleanup()