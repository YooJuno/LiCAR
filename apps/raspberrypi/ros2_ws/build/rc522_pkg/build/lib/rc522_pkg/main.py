#!/usr/bin/env python

'''
cmd
sudo /home/ssafy/juno/.venv/bin/python /home/ssafy/juno/main.py
'''
SERVO_STATE=False

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
import lgpio

# GPIO 모드 설정
GPIO.setmode(GPIO.BCM)  # BCM 번호 사용
GPIO.setwarnings(False)

# 서보모터 신호핀 설정 (예: GPIO 18)
servo1_pin = 13
servo2_pin = 19
GPIO.setup(servo1_pin, GPIO.OUT)
GPIO.setup(servo2_pin, GPIO.OUT)

# PWM 주파수 설정 (50Hz가 일반적)
pwm1 = GPIO.PWM(servo1_pin, 50)
pwm2 = GPIO.PWM(servo2_pin, 50)
pwm1.start(6.17)  # 초기 듀티 사이클 0%
pwm2.start(10.17)

reader = SimpleMFRC522()

#LED
CHIP = 0      # /dev/gpiochip0
LED1_PIN = 20 # 첫 번째 LED
LED2_PIN = 21 # 두 번째 LED

# gpiochip 열기
h = lgpio.gpiochip_open(CHIP)

# GPIO 20, 21을 출력으로 claim (초기값 0)
lgpio.gpio_claim_output(h, 0, LED1_PIN, 0)
lgpio.gpio_claim_output(h, 0, LED2_PIN, 0)

def set_angle(angle1, angle2):
    """서보 모터 각도 설정 함수"""
    duty1 = 2 + (angle1 / 18)  # 0~180도를 2~12% 듀티로 변환
    duty2 = 2 + (angle2 / 18)

    pwm1.ChangeDutyCycle(duty1)
    pwm2.ChangeDutyCycle(duty2)
    time.sleep(0.5)  # 모터가 이동할 시간 확보
    pwm1.ChangeDutyCycle(0)
    pwm2.ChangeDutyCycle(0)

def main():
    flag_nfc = False
    flag_yolo = True #원래는 False

    try:
        print("카드를 태그해주세요", flush=True)

        while True:
            id, text = reader.read()
            print(f"카드 ID: {id}", flush=True)
            #print(f"텍스트: {text}")

            if(id == 673075365188):
                # 카드 읽으면 서보 2개 움직이기
                # 예: servo1 90도, servo2 45도로 이동 후 원위치
                print("승인되었습니다\n", flush=True)

                if(flag_nfc == False):
                    set_angle(145,60)
                    time.sleep(1)
                    flag_nfc = True
                    print("모터 동작 완료\n", flush=True)
                    #YOLO 모델 코드
                    if(flag_yolo == True):
                        lgpio.gpio_write(h, LED1_PIN, 1)
                        lgpio.gpio_write(h, LED2_PIN, 0)
                        print("LED1 ON, LED2 OFF", flush=True)
                        time.sleep(1)

                        # LED1 OFF, LED2 ON
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
                    #GAZEBO랑 통신하는 코드
            else:
                print("접근이 거부되었습니다.\n", flush=True)
                time.sleep(1)
            
    except KeyboardInterrupt:
        print("프로그램 종료", flush=True)

    finally:
        pwm1.stop()
        pwm2.stop()
        # LED 끄기
        lgpio.gpio_write(h, LED1_PIN, 0)
        lgpio.gpio_write(h, LED2_PIN, 0)
    
        # 정리
        lgpio.gpiochip_close(h)
        GPIO.cleanup()

if __name__ == "__main__":
    main()