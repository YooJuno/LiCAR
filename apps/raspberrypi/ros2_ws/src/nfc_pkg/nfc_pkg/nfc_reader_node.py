#!/home/ssafy/juno/.venv/bin/python

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import time
import threading

CARD_ID_TO_USE = "673075365188"

class NfcReaderNode(Node):
    def __init__(self):
        super().__init__('nfc_reader_node')
        
        self.tag_publisher_ = self.create_publisher(String, 'nfc_tag', 10)
        self.reader = SimpleMFRC522()
        
        self.thread = threading.Thread(target=self.nfc_reading_loop, daemon=True)
        self.thread.start()
        
        self.get_logger().info('NFC Reader Node has been started.')

    def nfc_reading_loop(self):
        while rclpy.ok():
            self.get_logger().info('Ready to read a card.')
            try:
                # 카드가 태그될 때까지 기다림
                id = self.reader.read_id()
                
                # 유효한 카드 ID일 경우에만 토픽 발행
                if id and str(id) == CARD_ID_TO_USE:
                    self.get_logger().info(f'Valid card tagged: {id}. Publishing to /nfc_tag.')
                    msg = String()
                    msg.data = str(id)
                    self.tag_publisher_.publish(msg)
                    
                    # 한 번 태그 후, 2초간 동일한 태그를 무시하기 위한 딜레이
                    time.sleep(2.0)

            except Exception:
                # 에러 발생 시 잠시 후 다시 시도
                time.sleep(0.5)

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