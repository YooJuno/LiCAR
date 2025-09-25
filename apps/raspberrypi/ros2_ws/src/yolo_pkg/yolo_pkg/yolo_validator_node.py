#!/home/ssafy/juno/.venv/bin/python

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from ultralytics import YOLO
import paho.mqtt.client as mqtt # MQTT 클라이언트 라이브러리 import
import cv2
import json
import torch
import os
import requests

# 시스템의 상태를 명확하게 정의
class SystemState:
    IDLE = 0          # 대기 중 (첫 번째 태그를 기다림)
    VALIDATING = 1    # 검증 중
    VALIDATION_DONE = 2 # 검증 완료 (두 번째 태그를 기다림)
    WAITING_FOR_DRUGS = 3 # API 응답 대기 상태 추가

# MQTT 설정
MQTT_BROKER_URL = "192.168.100.157"
MQTT_PORT = 1883 # 일반적으로 MQTT는 1883, WebSocket은 다른 포트(예: 9001)를 사용. BE 서버 설정 확인 필요
MQTT_TOPIC_REQUEST = "robots/status/1"
MQTT_TOPIC_RESPONSE = "robots/response/1"

class YoloValidatorNode(Node):
    def __init__(self):
        super().__init__('yolo_validator_node')
        
        self.nfc_tag_subscription = self.create_subscription(String, 'nfc_tag', self.nfc_tag_callback, 10)
        
        # 3개의 명확한 명령 토픽을 발행
        self.open_publisher = self.create_publisher(Bool, 'open_door', 10)
        self.complete_publisher = self.create_publisher(Bool, 'validation_complete_signal', 10)
        self.close_publisher = self.create_publisher(Bool, 'close_door', 10)
        
        self.current_state = SystemState.IDLE
        self.lock = threading.Lock() # 스레드 간 상태 공유를 위한 Lock

        # --- MQTT 클라이언트 설정 ---
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message

        try:
            # 일반적인 MQTT TCP 연결 (더 표준적)
            self.mqtt_client.connect(MQTT_BROKER_URL, MQTT_PORT, 60)
            self.mqtt_client.loop_start() # 별도의 스레드에서 MQTT 네트워크 루프 실행
        except Exception as e:
            self.get_logger().error(f"Failed to connect to MQTT Broker: {e}")

        try:
            self.device = 'cpu'
            model_path = '/home/ssafy/Desktop/best.pt'
            self.model = YOLO(model_path)
            self.model.to(self.device)
            self.class_names = self.model.names
            self.get_logger().info(f"Model loaded successfully from {model_path}")
        except Exception as e:
            self.get_logger().error(f"FATAL: Failed to load YOLO model: {e}")
            return

        self.cap = None
        try:
            self.get_logger().info("Attempting to open camera...")
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.get_logger().error("Cannot open camera.")
                self.cap = None
        except Exception as e:
            self.get_logger().error(f"Failed to initialize camera: {e}")
            self.cap = None
            
        self.target_pills = {}
        
        self.timer = self.create_timer(0.1, self.process_frame)
        self.get_logger().info('YOLO Validator Node has been started. Current state: IDLE')

 ################################### 통신 코드 ######################################      
    def on_mqtt_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            self.get_logger().info("Connected successfully to MQTT Broker.")
            # 연결 성공 시, 응답 토픽을 구독
            client.subscribe(MQTT_TOPIC_RESPONSE)
            self.get_logger().info(f"Subscribed to MQTT topic: {MQTT_TOPIC_RESPONSE}")
        else:
            self.get_logger().error(f"Failed to connect to MQTT Broker, return code {rc}\n")


#################################### NFC 태그 코드 ######################################
    def nfc_tag_callback(self, msg):
        """NFC 태그 신호를 받았을 때, 현재 시스템 상태에 따라 다른 동작을 수행합니다."""
        if self.current_state == SystemState.IDLE:
            if self.cap is None:
                self.get_logger().error("Cannot start validation because camera is not available.")
                return

            self.get_logger().info("First NFC tag received. Starting validation process.")
            try:
                self.get_logger().info(f"Requesting drug list from: {API_ENDPOINT}")
                response = requests.get(API_ENDPOINT, timeout=5)

                if response.status_code == 200:
                    drug_names = [drug['name'] for drug in response.json()]
                    self.get_logger().info(f"SUCCESS: Received drug list: {drug_names}")
                    
                    self.target_pills = {name: False for name in drug_names}
                    self.current_state = SystemState.VALIDATING
                    
                    # "문 열어라" 명령 발행
                    open_msg = Bool(); open_msg.data = True
                    self.open_publisher.publish(open_msg)
                    self.get_logger().info("Published command to open the door.")
                else:
                    self.get_logger().error(f"API Error. Status Code: {response.status_code}")

            except requests.exceptions.RequestException as e:
                self.get_logger().error(f"API request failed: {e}")

        elif self.current_state == SystemState.VALIDATION_DONE:
            self.get_logger().info("Second NFC tag received. Commanding door to close.")
            # "문 닫아라" 명령 발행
            close_msg = Bool(); close_msg.data = True
            self.close_publisher.publish(close_msg)
            
            # 모든 상태를 초기화하여 다음 프로세스 준비
            self.current_state = SystemState.IDLE
            self.target_pills = {}

    def process_frame(self):
        if self.current_state != SystemState.VALIDATING or not self.cap:
            return
            
        ret, frame = self.cap.read()
        if not ret: return
        
        results_generator = self.model(frame, stream=True, verbose=False, conf=0.25, device=self.device, imgsz=192)
        
        for results in results_generator:
            for box in results.boxes:
                class_id = int(box.cls[0])
                pill_name = self.class_names.get(class_id, "Unknown")
                
                if pill_name in self.target_pills and not self.target_pills[pill_name]:
                    self.target_pills[pill_name] = True
                    self.get_logger().info(f"Found Target: {pill_name}! Status: {self.target_pills}")

        if self.target_pills and all(self.target_pills.values()):
            self.get_logger().info('SUCCESS: All target drugs have been detected! Waiting for final tag.')
            self.current_state = SystemState.VALIDATION_DONE
            
            # "검증 완료" 신호 발행
            complete_msg = Bool(); complete_msg.data = True
            self.complete_publisher.publish(complete_msg)

    def destroy_node(self):
        if self.cap: self.cap.release()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    yolo_validator_node = YoloValidatorNode()
    try: rclpy.spin(yolo_validator_node)
    except KeyboardInterrupt: pass
    finally:
        yolo_validator_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()