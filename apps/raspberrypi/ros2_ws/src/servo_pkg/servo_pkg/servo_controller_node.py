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
        
        # 구독자
        self.validation_subscription = self.create_subscription(
            Bool,
            'validation_status',
            self.validation_status_callback,
            10)
        
        # --- 추가된 부분: 완료 상태를 발행할 새로운 Publisher ---
        self.delivery_status_publisher_ = self.create_publisher(
            Int32, 
            'delivery_status', # 새로운 토픽 이름
            10)

        # 문의 현재 상태를 기억하는 변수
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

    def validation_status_callback(self, msg):
        if msg.data: # True 신호 수신
            if self.is_door_open:
                # 문이 열려있을 때 True 신호 -> "검증 성공, 최종 태그 대기"
                self.get_logger().info('Validation SUCCESS. Turn on green light and wait for final tag.')
                lgpio.gpio_write(self.h, self.LED_GREEN_PIN, 1)
            else:
                # 문이 닫혀있을 때 True 신호 -> "두 번째 태그로 인한 최종 닫힘 명령"
                self.get_logger().info('Final confirmation received. Closing the door.')
                lgpio.gpio_write(self.h, self.LED_GREEN_PIN, 0)
                self.set_angle(90) # 문 닫는 각도
                self.is_door_open = False
                
                # --- 추가된 부분: 문을 닫은 후, 완료 코드 발행 ---
                status_code_msg = Int32()
                # 나중에는 이 값을 BE 서버로부터 받아온 변수로 채우게 됩니다.
                status_code_msg.data = 301 
                self.delivery_status_publisher_.publish(status_code_msg)
                self.get_logger().info(f'Published delivery status code: {status_code_msg.data}')

        else: # False 신호 수신 (검증 시작)
            if not self.is_door_open:
                self.get_logger().info('Validation START received. Opening the door.')
                lgpio.gpio_write(self.h, self.LED_GREEN_PIN, 0)
                self.set_angle(0) # 문 여는 각도
                self.is_door_open = True
            else:
                pass

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
    except KeyboardInterrupt: pass
    finally:
        servo_controller_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()