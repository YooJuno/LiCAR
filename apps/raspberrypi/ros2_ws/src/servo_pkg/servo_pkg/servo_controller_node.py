#!/home/ssafy/juno/.venv/bin/python

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
import RPi.GPIO as GPIO
import lgpio
import time

class ServoControllerNode(Node):
    def __init__(self):
        super().__init__('servo_controller_node')
        
        self.validation_subscription = self.create_subscription(
            Bool,
            'validation_status',
            self.validation_status_callback,
            10)
        
        # --- 추가된 부분: 문의 현재 상태를 기억하는 변수 ---
        # True = 열림, False = 닫힘. 초기 상태는 '닫힘'
        self.is_door_open = False
        
        # --- 하드웨어 초기화 (이전과 동일) ---
        GPIO.setmode(GPIO.BCM)
        self.servo_pin = 13 
        GPIO.setup(self.servo_pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.servo_pin, 50)
        self.pwm.start(0)

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

    # --- 수정된 부분: 상태를 확인하는 콜백 함수 로직 ---
    def validation_status_callback(self, msg):
        """YOLO 검증 결과에 따라, 문의 현재 상태를 확인하고 필요할 때만 동작합니다."""
        if msg.data: # True: 검증 성공 (문을 닫아야 함)
            # 문이 이미 닫혀있으면 아무것도 하지 않음
            if not self.is_door_open:
                self.get_logger().info('System is Ready or already Validated. Door remains closed.')
                return
            
            # 문이 열려있을 때만 닫는 동작을 수행
            self.get_logger().info('Validation SUCCESS received. Closing the door.')
            lgpio.gpio_write(self.h, self.LED_GREEN_PIN, 1)
            self.set_angle(90) # 문 닫는 각도
            self.is_door_open = False # 상태 업데이트: 문이 닫힘

        else: # False: 검증 시작 (문을 열어야 함)
            # 문이 이미 열려있으면 아무것도 하지 않음
            if self.is_door_open:
                self.get_logger().info('Validation already in progress. Door remains open.')
                return

            # 문이 닫혀있을 때만 여는 동작을 수행
            self.get_logger().info('Validation START received. Opening the door.')
            lgpio.gpio_write(self.h, self.LED_GREEN_PIN, 0)
            self.set_angle(0) # 문 여는 각도
            self.is_door_open = True # 상태 업데이트: 문이 열림

    def destroy_node(self):
        # ... (이전과 동일)
        self.pwm.stop()
        GPIO.cleanup()
        lgpio.gpio_write(self.h, self.LED_GREEN_PIN, 0)
        lgpio.gpiochip_close(self.h)
        super().destroy_node()

def main(args=None):
    # ... (이전과 동일)
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