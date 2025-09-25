#!/home/ssafy/juno/.venv/bin/python

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, Int32 # Int32 메시지 타입을 추가
import RPi.GPIO as GPIO
import lgpio
import time

class ServoControllerNode(Node):
    def __init__(self):
        super().__init__('servo_controller_node')
        
        # --- 수정: 3개의 명확한 명령 토픽을 구독 ---
        self.open_subscription = self.create_subscription(
            Bool, 'open_door', self.open_door_callback, 10)
        self.complete_subscription = self.create_subscription(
            Bool, 'validation_complete_signal', self.validation_complete_callback, 10)
        self.close_subscription = self.create_subscription(
            Bool, 'close_door', self.close_door_callback, 10)
        
        # --- 추가: 완료 상태를 발행할 새로운 Publisher ---
        self.delivery_status_publisher_ = self.create_publisher(
            Int32, 'delivery_status', 10)
            
        # --- 하드웨어 초기화 (이전과 동일) ---
        GPIO.setmode(GPIO.BCM)

        # 첫 번째 서보모터 (GPIO 13)
        self.servo1_pin = 13
        GPIO.setup(self.servo1_pin, GPIO.OUT)
        self.pwm1 = GPIO.PWM(self.servo1_pin, 50)
        self.pwm1.start(0) # 듀티 사이클 0으로 시작

        # 두 번째 서보모터 (GPIO 19)
        self.servo2_pin = 19
        GPIO.setup(self.servo2_pin, GPIO.OUT)
        self.pwm2 = GPIO.PWM(self.servo2_pin, 50)
        self.pwm2.start(0) # 듀티 사이클 0으로 시작

        self.CHIP = 0
        self.LED_GREEN_PIN = 20
        self.h = lgpio.gpiochip_open(self.CHIP)
        lgpio.gpio_claim_output(self.h, 0, self.LED_GREEN_PIN, 0)
        
        self.get_logger().info('Servo Controller Node has been started.')

    def set_angles(self, angle1, angle2):
        """두 개의 서보 모터를 각각의 목표 각도로 이동시킵니다."""
        duty1 = 2 + (angle1 / 18)
        duty2 = 2 + (angle2 / 18)

        self.get_logger().info(f"Moving servos to angles: ({angle1}, {angle2}) with duties: ({duty1:.2f}, {duty2:.2f})")
        
        # 두 모터에 동시에 PWM 신호 변경
        self.pwm1.ChangeDutyCycle(duty1)
        self.pwm2.ChangeDutyCycle(duty2)
        
        # 모터가 움직일 시간을 충분히 줌
        time.sleep(1.5)
        
        # 모터 떨림 방지를 위해 신호 중지 (듀티 사이클 0으로)
        self.pwm1.ChangeDutyCycle(0)
        self.pwm2.ChangeDutyCycle(0)


    # --- 수정: 각 명령에 맞는 콜백 함수들 ---
    def open_door_callback(self, msg):
        if msg.data:
            self.get_logger().info('Open command received. Opening the door.')
            lgpio.gpio_write(self.h, self.LED_GREEN_PIN, 0) # 문 열 때는 LED 끄기
            self.set_angles(20, 160) # 문 여는 각도

    def validation_complete_callback(self, msg):
        if msg.data:
            self.get_logger().info('Validation complete signal received. Turning on green light.')
            lgpio.gpio_write(self.h, self.LED_GREEN_PIN, 1) # 초록 LED 켜기

    def close_door_callback(self, msg):
        if msg.data:
            self.get_logger().info('Close command received. Closing the door.')
            lgpio.gpio_write(self.h, self.LED_GREEN_PIN, 0) # 문 닫을 땐 LED 끄기
            self.set_angles(90,90) # 문 닫는 각도

            # --- 추가: 문을 닫은 후, 완료 코드 발행 ---
            status_code_msg = Int32()
            status_code_msg.data = 301 
            self.delivery_status_publisher_.publish(status_code_msg)
            self.get_logger().info(f'Published delivery status code: {status_code_msg.data}')

    def destroy_node(self):
        self.pwm1.stop()
        self.pwm2.stop()
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