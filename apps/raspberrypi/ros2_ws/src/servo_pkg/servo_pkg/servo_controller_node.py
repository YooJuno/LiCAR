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
        
        # 3개의 명확한 명령 토픽을 구독
        self.open_subscription = self.create_subscription(
            Bool, 'open_door', self.open_door_callback, 10)
        self.complete_subscription = self.create_subscription(
            Bool, 'validation_complete_signal', self.validation_complete_callback, 10)
        self.close_subscription = self.create_subscription(
            Bool, 'close_door', self.close_door_callback, 10)
        
        # --- 하드웨어 초기화 ---
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

    def open_door_callback(self, msg):
        if msg.data:
            self.get_logger().info('Open command received. Opening the door.')
            lgpio.gpio_write(self.h, self.LED_GREEN_PIN, 0) # 문 열 때는 LED 끄기
            self.set_angle(0) # 문 여는 각도

    def validation_complete_callback(self, msg):
        if msg.data:
            self.get_logger().info('Validation complete signal received. Turning on green light.')
            lgpio.gpio_write(self.h, self.LED_GREEN_PIN, 1) # 초록 LED 켜기

    def close_door_callback(self, msg):
        if msg.data:
            self.get_logger().info('Close command received. Closing the door.')
            lgpio.gpio_write(self.h, self.LED_GREEN_PIN, 0) # 문 닫을 땐 LED 끄기
            self.set_angle(90) # 문 닫는 각도

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