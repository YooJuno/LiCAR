#런치 코드: ros2 launch rc522_pkg main_launch.py

#!/usr/bin/env python

import rclpy
from rclpy.node import Node
from my_interfaces.msg import StartSignal  # 커스텀 메시지
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
import lgpio
from picamera2 import Picamera2

SERVO_STATE=False

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
servo1_pin = 13
servo2_pin = 19
GPIO.setup(servo1_pin, GPIO.OUT)
GPIO.setup(servo2_pin, GPIO.OUT)
pwm1 = GPIO.PWM(servo1_pin, 50)
pwm2 = GPIO.PWM(servo2_pin, 50)
pwm1.start(6.17)
pwm2.start(10.17)

reader = SimpleMFRC522()

CHIP = 0
LED1_PIN = 20
LED2_PIN = 21
h = lgpio.gpiochip_open(CHIP)
lgpio.gpio_claim_output(h, 0, LED1_PIN, 0)
lgpio.gpio_claim_output(h, 0, LED2_PIN, 0)

def set_angle(angle1, angle2):
    duty1 = 2 + (angle1 / 18)
    duty2 = 2 + (angle2 / 18)
    pwm1.ChangeDutyCycle(duty1)
    pwm2.ChangeDutyCycle(duty2)
    time.sleep(0.5)
    pwm1.ChangeDutyCycle(0)
    pwm2.ChangeDutyCycle(0)

# --- ROS 2 노드 클래스 ---
class StartSignalPublisher(Node):
    def __init__(self):
        super().__init__('start_signal_publisher')
        self.publisher_ = self.create_publisher(StartSignal, 'start_signal', 10)

    def send_start_signal(self):
        msg = StartSignal()
        msg.start = True
        self.publisher_.publish(msg)
        self.get_logger().info("Start signal sent!")

def main():
    rclpy.init()
    ros_node = StartSignalPublisher()

    flag_nfc = False
    flag_yolo = True

    try:
        print("카드를 태그해주세요", flush=True)

        while True:
            id, text = reader.read()
            print(f"카드 ID: {id}", flush=True)

            if id == 673075365188:
                print("승인되었습니다\n", flush=True)

                if not flag_nfc:
                    set_angle(145,60)
                    time.sleep(1)
                    flag_nfc = True
                    print("모터 동작 완료\n", flush=True)

                    if flag_yolo:
                        lgpio.gpio_write(h, LED1_PIN, 1)
                        lgpio.gpio_write(h, LED2_PIN, 0)
                        print("LED1 ON, LED2 OFF", flush=True)
                        time.sleep(1)
                        lgpio.gpio_write(h, LED1_PIN, 0)
                        lgpio.gpio_write(h, LED2_PIN, 1)
                        print("LED1 OFF, LED2 ON", flush=True)
                        time.sleep(1)

                else:
                    set_angle(65,147)
                    time.sleep(1)
                    flag_nfc = False
                    print("모터 동작 완료\n", flush=True)
                    print("LiCAR가 배달 중입니다...", flush=True)

                    # =====================
                    # 여기서 출발 신호를 보내야함
                    # =====================
                    ros_node.send_start_signal()

            else:
                print("접근이 거부되었습니다.\n", flush=True)
                time.sleep(1)

    except KeyboardInterrupt:
        print("프로그램 종료", flush=True)

    finally:
        pwm1.stop()
        pwm2.stop()
        lgpio.gpio_write(h, LED1_PIN, 0)
        lgpio.gpio_write(h, LED2_PIN, 0)
        lgpio.gpiochip_close(h)
        GPIO.cleanup()
        ros_node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
