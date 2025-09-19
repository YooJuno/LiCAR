#!/home/ssafy/juno/.venv/bin/python

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import requests
import json
import time
import threading

# --- 수정된 부분: API 엔드포인트를 원래대로 복원 ---
API_ENDPOINT = "http://192.168.100.157:8080/api/v1/deliveries/requested-drugs"
CARD_ID_TO_USE = "673075365188" # 사용할 유일한 카드 ID (여전히 검증용으로 사용)

class NfcReaderNode(Node):
    def __init__(self):
        super().__init__('nfc_reader_node')
        
        self.publisher_ = self.create_publisher(String, 'drug_list_request', 10)
        self.reader = SimpleMFRC522()
        
        self.is_system_busy = True
        self.lock = threading.Lock()

        self.status_subscription = self.create_subscription(
            Bool, 
            'validation_status', 
            self.validation_status_callback, 
            10)

        self.thread = threading.Thread(target=self.nfc_reading_loop, daemon=True)
        self.thread.start()
        
        self.get_logger().info('NFC Reader Node has been started. Waiting for system to be ready...')

    def validation_status_callback(self, msg):
        with self.lock:
            self.is_system_busy = not msg.data 

        if self.is_system_busy:
            self.get_logger().info("System is now BUSY (validation in progress). NFC reading is paused.")
        else:
            self.get_logger().info("System is now READY. NFC reading is resumed.")

    def nfc_reading_loop(self):
        self.get_logger().info("NFC thread started. Initializing reader with a 3-second delay...")
        time.sleep(3.0)

        while rclpy.ok():
            if not self.is_system_busy:
                self.get_logger().info('Ready to read a new card. Waiting for a tag...')
                try:
                    id = self.reader.read_id()
                    
                    if not id:
                        continue
                    
                    self.get_logger().info(f'Card ID: {id} detected!')
                    
                    if str(id) == CARD_ID_TO_USE:
                        with self.lock:
                            self.is_system_busy = True
                        
                        self.get_logger().info("Valid card detected. System is now BUSY.")

                        try:
                            # --- 수정된 부분: ID를 포함하지 않는 원래 주소로 요청 ---
                            self.get_logger().info(f"Requesting drug list from: {API_ENDPOINT}")
                            response = requests.get(API_ENDPOINT, timeout=5)

                            if response.status_code == 200:
                                drugs_data = response.json()
                                drug_names = [drug['name'] for drug in drugs_data]
                                self.get_logger().info(f"SUCCESS: Received drug list: {drug_names}")

                                msg = String()
                                msg.data = json.dumps(drug_names)
                                self.publisher_.publish(msg)
                                self.get_logger().info(f"Published to /drug_list_request.")

                            else:
                                self.get_logger().error(f"API Error. Status Code: {response.status_code}")
                                with self.lock:
                                    self.is_system_busy = False

                        except requests.exceptions.RequestException as e:
                            self.get_logger().error(f"API request failed: {e}")
                            with self.lock:
                                self.is_system_busy = False
                    else:
                        self.get_logger().warn(f"Ignored an unauthorized card: {id}")

                except Exception:
                    pass
            else:
                time.sleep(1.0)


def main(args=None):
    rclpy.init(args=args)
    nfc_reader_node = NfcReaderNode()
    try:
        rclpy.spin(nfc_reader_node)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
        nfc_reader_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()