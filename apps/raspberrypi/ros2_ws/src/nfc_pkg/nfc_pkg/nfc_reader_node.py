#!/home/ssafy/juno/.venv/bin/python

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import requests  # API 요청을 위한 라이브러리
import json      # Python 리스트를 JSON 문자열로 변환하기 위한 라이브러리
import time

# 요청을 보낼 Spring BE 서버의 주소
API_ENDPOINT = "http://192.168.100.157:8080/api/v1/deliveries/requested-drugs"

class NfcReaderNode(Node):
    def __init__(self):
        super().__init__('nfc_reader_node')
        
        # 발행할 토픽 이름을 '/drug_list_request'로 변경. 약품 목록(JSON 문자열)을 발행.
        self.publisher_ = self.create_publisher(String, 'drug_list_request', 10)
        
        # 동일한 카드를 계속해서 읽고 API를 호출하는 것을 방지하기 위한 변수
        self.last_read_id = None
        self.read_cooldown = 5.0  # 5초의 쿨다운 시간
        self.last_read_time = 0

        self.reader = SimpleMFRC522()
        self.timer = self.create_timer(0.5, self.read_nfc_and_fetch_drugs) # 0.5초마다 실행
        self.get_logger().info('NFC Reader Node has been started. Waiting for card...')

    def read_nfc_and_fetch_drugs(self):
        try:
            # non-blocking read 시도
            id = self.reader.read_id_no_block()
            if not id:
                # 카드가 없으면 아무것도 하지 않음
                return

            current_time = time.time()
            # 마지막으로 읽은 카드와 같고, 쿨다운 시간이 지나지 않았으면 무시
            if id == self.last_read_id and (current_time - self.last_read_time) < self.read_cooldown:
                return

            # 새로운 카드가 인식됨
            self.get_logger().info(f'Card ID: {id} detected!')
            self.last_read_id = id
            self.last_read_time = current_time

            # --- API 서버에 GET 요청 보내기 ---
            try:
                self.get_logger().info(f"Requesting drug list from: {API_ENDPOINT}")
                response = requests.get(API_ENDPOINT, timeout=5) # 5초 타임아웃

                # 요청이 성공했는지 확인 (HTTP 상태 코드 200)
                if response.status_code == 200:
                    drugs_data = response.json() # JSON 응답을 Python 객체(리스트)로 변환
                    
                    # 약품 이름만 추출하여 새로운 리스트 생성
                    drug_names = [drug['name'] for drug in drugs_data]
                    self.get_logger().info(f"Received drug list: {drug_names}")

                    # Python 리스트를 JSON 형식의 '문자열'로 변환
                    # 예: ["아스피린", "타이레놀"] -> '["아스피린", "타이레놀"]'
                    json_string_payload = json.dumps(drug_names)

                    # ROS 메시지에 담아서 발행
                    msg = String()
                    msg.data = json_string_payload
                    self.publisher_.publish(msg)
                    self.get_logger().info(f"Published to /drug_list_request: {msg.data}")

                else:
                    self.get_logger().error(
                        f"Failed to get drug list. Status Code: {response.status_code}, Response: {response.text}")

            except requests.exceptions.RequestException as e:
                self.get_logger().error(f"API request failed: {e}")

        except Exception as e:
            # mfrc522 라이브러리에서 발생할 수 있는 다른 예외 처리
            self.get_logger().warn(f"An error occurred during NFC read: {e}")


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