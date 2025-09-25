#!/home/ssafy/juno/.venv/bin/python

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from ultralytics import YOLO
import paho.mqtt.client as mqtt
import cv2
import json
import torch
import os
import threading

class SystemState:
    IDLE = 0
    WAITING_FOR_DRUGS = 1
    VALIDATING = 2
    VALIDATION_DONE = 3

# MQTT 설정
MQTT_WS_URL = "192.168.100.157"
MQTT_WS_PORT = 9001 # BE 서버의 실제 WebSocket 포트
MQTT_WS_PATH = "/mqtt"
MQTT_TOPIC_REQUEST_DRUGS = "robots/status/1"
MQTT_TOPIC_RESPONSE_DRUGS = "robots/response/1"
# --- 추가: 인식 결과 전송을 위한 토픽 ---
MQTT_TOPIC_RECOGNITION_UPDATE = "transports/recognition/update"
MQTT_USERNAME = "robot"
MQTT_PASSWORD = os.environ["MQTT_PASSWORD"]

class YoloValidatorNode(Node):
    def __init__(self):
        super().__init__('yolo_validator_node')
        
        self.nfc_tag_subscription = self.create_subscription(String, 'nfc_tag', self.nfc_tag_callback, 10)
        self.open_publisher = self.create_publisher(Bool, 'open_door', 10)
        self.complete_publisher = self.create_publisher(Bool, 'validation_complete_signal', 10)
        self.close_publisher = self.create_publisher(Bool, 'close_door', 10)
        
        self.current_state = SystemState.IDLE
        self.lock = threading.Lock()
        
        # --- 추가/수정: 데이터 저장을 위한 변수 ---
        self.transport_id = None
        self.drug_id_map = {} # 예: {'씨엠지쎄파클러캡슐': 1}
        self.target_pills = {} # 예: {'씨엠지쎄파클러캡슐': False}

        # MQTT 클라이언트 설정
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport="websockets")
        self.mqtt_client.ws_set_options(path=MQTT_WS_PATH)
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        self.mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

        try:
            self.get_logger().info(f"Connecting to MQTT Broker at ws://{MQTT_WS_URL}:{MQTT_WS_PORT}{MQTT_WS_PATH}...")
            self.mqtt_client.connect(MQTT_WS_URL, MQTT_WS_PORT, 60)
            self.mqtt_client.loop_start()
        except Exception as e:
            self.get_logger().error(f"Failed to connect to MQTT Broker: {e}")

        # ... (이하 모델, 카메라 초기화는 이전과 동일)
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
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened(): self.cap = None
        except Exception: self.cap = None
        
        self.timer = self.create_timer(0.1, self.process_frame)
        self.get_logger().info('YOLO Validator Node has been started. Current state: IDLE')

    def on_mqtt_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            self.get_logger().info("Connected successfully to MQTT Broker.")
            client.subscribe(MQTT_TOPIC_RESPONSE_DRUGS)
            self.get_logger().info(f"Subscribed to MQTT topic: {MQTT_TOPIC_RESPONSE_DRUGS}")
        else:
            self.get_logger().error(f"Failed to connect to MQTT Broker, return code {rc}")

    def on_mqtt_message(self, client, userdata, msg):
        """MQTT 브로커로부터 약품 목록 응답을 수신합니다."""
        with self.lock:
            if self.current_state == SystemState.WAITING_FOR_DRUGS:
                try:
                    payload_str = msg.payload.decode('utf-8')
                    self.get_logger().info(f"Received message from MQTT topic '{msg.topic}': {payload_str}")
                    
                    data = json.loads(payload_str)
                    
                    # --- 수정: transportId와 drugId 매핑 정보 저장 ---
                    self.transport_id = data.get('transportId')
                    drugs_list = data.get('drugs', [])
                    
                    if not self.transport_id or not drugs_list:
                        self.get_logger().error("Invalid data format received from server.")
                        self.current_state = SystemState.IDLE
                        return

                    drug_names = []
                    for drug in drugs_list:
                        drug_name = drug.get('name')
                        drug_id = drug.get('drugId')
                        if drug_name and drug_id:
                            drug_names.append(drug_name)
                            self.drug_id_map[drug_name] = drug_id
                    
                    self.target_pills = {name: False for name in drug_names}
                    self.current_state = SystemState.VALIDATING
                    
                    self.get_logger().info(f"Validation started. Transport ID: {self.transport_id}, Drug ID Map: {self.drug_id_map}")
                    
                    open_msg = Bool(); open_msg.data = True
                    self.open_publisher.publish(open_msg)
                    self.get_logger().info("Published command to open the door.")
                except Exception as e:
                    self.get_logger().error(f"Error processing MQTT message: {e}")
                    self.current_state = SystemState.IDLE

    def nfc_tag_callback(self, msg):
        with self.lock:
            if self.current_state == SystemState.IDLE:
                if self.cap is None:
                    self.get_logger().error("Cannot start validation because camera is not available.")
                    return

                self.get_logger().info("First NFC tag received. Requesting drug list via MQTT...")
                self.mqtt_client.publish(MQTT_TOPIC_REQUEST_DRUGS, payload="get_list")
                self.current_state = SystemState.WAITING_FOR_DRUGS

            elif self.current_state == SystemState.VALIDATION_DONE:
                self.get_logger().info("Second NFC tag received. Commanding door to close.")
                close_msg = Bool(); close_msg.data = True
                self.close_publisher.publish(close_msg)
                
                # 모든 상태 초기화
                self.current_state = SystemState.IDLE
                self.transport_id = None
                self.drug_id_map = {}
                self.target_pills = {}

    def process_frame(self):
        with self.lock:
            if self.current_state != SystemState.VALIDATING or not self.cap:
                return
        
        ret, frame = self.cap.read()
        if not ret: return
        
        results_generator = self.model(frame, stream=True, verbose=False, conf=0.25, device=self.device, imgsz=192)
        
        for results in results_generator:
            for box in results.boxes:
                class_id = int(box.cls[0])
                pill_name = self.class_names.get(class_id, "Unknown")
                
                # --- 수정된 부분: 약품 인식 시 MQTT 메시지 발행 ---
                if pill_name in self.target_pills and not self.target_pills[pill_name]:
                    with self.lock:
                        self.target_pills[pill_name] = True
                    self.get_logger().info(f"Found Target: {pill_name}! Status: {self.target_pills}")
                    
                    # 전송할 데이터 생성
                    drug_id_to_send = self.drug_id_map.get(pill_name)
                    if self.transport_id is not None and drug_id_to_send is not None:
                        payload_to_send = {
                            "transportId": self.transport_id,
                            "drugId": drug_id_to_send
                        }
                        # JSON 문자열로 변환하여 발행
                        self.mqtt_client.publish(MQTT_TOPIC_RECOGNITION_UPDATE, json.dumps(payload_to_send))
                        self.get_logger().info(f"Published recognition update: {payload_to_send}")

        with self.lock:
            if self.target_pills and all(self.target_pills.values()):
                self.get_logger().info('SUCCESS: All target drugs have been detected! Waiting for final tag.')
                self.current_state = SystemState.VALIDATION_DONE
                
                complete_msg = Bool(); complete_msg.data = True
                self.complete_publisher.publish(complete_msg)

    def destroy_node(self):
        self.mqtt_client.loop_stop()
        if self.cap: self.cap.release()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    yolo_validator_node = YoloValidatorNode()
    try: 
        rclpy.spin(yolo_validator_node)
    except KeyboardInterrupt: pass
    finally:
        yolo_validator_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()