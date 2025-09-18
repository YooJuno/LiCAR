#!/home/ssafy/juno/.venv/bin/python

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String # String 메시지 타입을 추가
import RPi.GPIO as GPIO
import lgpio
import time

class ServoControllerNode(Node):
    def __init__(self):
        super().__init__('servo_controller_node')
        
        # --- 수정된 부분: 구독자 2개로 변경 ---
        # 1. YOLO 검증 결과를 구독
        self.validation_subscription = self.create_subscription(
            Bool,
            'validation_status',
            self.validation_status_callback,
            10)
            
        # 2. NFC 태그 신호 (약품 목록 요청)를 구독
        self.request_subscription = self.create_subscription(
            String,
            'drug_list_request',
            self.open_door_callback,
            10)
        
        # --- 하드웨어 초기화 ---
        GPIO.setmode(GPIO.BCM)
        # TODO: 실제 서보모터 핀 번호로 수정
        self.servo_pin = 13 
        GPIO.setup(self.servo_pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.servo_pin, 50)
        self.pwm.start(0)

        # LED
        self.CHIP = 0
        self.LED_GREEN_PIN = 20
        self.h = lgpio.gpiochip_open(self.CHIP)
        lgpio.gpio_claim_output(self.h, 0, self.LED_GREEN_PIN, 0)
        
        self.get_logger().info('Servo Controller Node has been started.')

    def set_angle(self, angle):
        duty = 2 + (angle / 18)
        self.pwm.ChangeDutyCycle(duty)
        time.sleep(1)
        self.pwm.ChangeDutyCycle(0)

    # --- 추가된 부분: 문 여는 콜백 함수 ---
    def open_door_callback(self, msg):
        """NFC 태그 신호를 받으면 문을 엽니다."""
        # msg.data가 비어있지 않은지 확인 (정상적인 요청인지)
        if msg.data and msg.data != "[]":
            self.get_logger().info('NFC tag detected. Opening the door...')
            # TODO: 실제 문 여는 각도로 수정
            self.set_angle(0) 
            # LED를 초기 상태(OFF)로 설정
            lgpio.gpio_write(self.h, self.LED_GREEN_PIN, 0)

    def validation_status_callback(self, msg):
        """YOLO 검증 결과에 따라 문을 닫거나 피드백을 줍니다."""
        if msg.data: # True: 성공
            self.get_logger().info('Validation SUCCESS received. Closing the door.')
            lgpio.gpio_write(self.h, self.LED_GREEN_PIN, 1) # 초록 LED ON
            # TODO: 실제 문 닫는 각도로 수정
            self.set_angle(90) 
        else: # False: 실패 (또는 검증 시작 신호)
            self.get_logger().warn('Validation in progress or failed. Keeping door open.')
            lgpio.gpio_write(self.h, self.LED_GREEN_PIN, 0) # 초록 LED OFF

    def destroy_node(self):
        self.pwm.stop()
        GPIO.cleanup()
        lgpio.gpio_write(self.h, self.LED_GREEN_PIN, 0)
        lgpio.gpiochip_close(self.h)
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    servo_controller_node = ServoControllerNode()
    try:
        rclpy.spin(servo_controller_node)
    except KeyboardInterrupt:
        pass
    finally:
        servo_controller_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()