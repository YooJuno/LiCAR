#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32, Bool, String
import subprocess
import os

class TurtlebotMain(Node):
    def __init__(self):
        super().__init__('turtlebot_main_node')

        # 목적지 신호를 수신하는 구독자
        self.create_subscription(Int32, '/turtlebot_target', self.target_callback, 10)
        # 엘리베이터 문 상태를 수신하는 구독자
        self.create_subscription(Bool, '/elevator/door_state', self.door_callback, 10)
        # mover 완료 신호를 수신하는 구독자
        self.create_subscription(Bool, '/turtlebot/move_complete', self.move_complete_callback, 10)

        # 목적지 신호를 mover로 보내는 퍼블리셔
        self.mover_pub = self.create_publisher(Int32, '/turtlebot_command', 10)
        # 도착 신호 퍼블리셔
        self.arrival_pub = self.create_publisher(Bool, '/turtlebot/arrived', 10)

        # 상태 변수
        self.door_triggered = False
        self.route = []
        self.current_step = 0
        self.pending_target = None
        self.waiting_for_elevator = False  # 2자리 신호 후 엘리베이터 대기 상태
        self.elevator_timer = None  # 3초 대기 타이머
        self.last_sent_command = None  # 마지막으로 보낸 명령 추적
        self.target_floor_data = None  # 목표 층 데이터 (엘리베이터 명령용)

        self.get_logger().info("✅ Main node ready, waiting for target...")

    def target_callback(self, msg: Int32):
        dest = msg.data
        self.get_logger().info(f"🎯 목적지 요청 수신: {dest}")

        # 신호 검증: 0 또는 01,02로 끝나는 3자리 숫자만 허용 (302 이하)
        if dest == 0:
            # 0번(의국)은 허용
            pass
        elif len(str(dest)) == 3:
            # 302 이하 정수 확인
            if dest > 302:
                self.get_logger().warn(f"범위 초과: {dest} (302 이하 숫자만 허용)")
                return
            # 3자리 숫자인 경우 01, 02로 끝나는지 확인
            last_two_digits = dest % 100
            if last_two_digits not in [1, 2]:  # 01 = 1, 02 = 2
                self.get_logger().warn(f"지원하지 않는 호실: {dest} (01, 02호만 지원)")
                return
        else:
            self.get_logger().warn(f"잘못된 신호 형식: {dest} (0 또는 3자리 숫자만 허용)")
            return

        # 새로운 목적지 요청이 들어오면 기존 작업 중단하고 재시작
        # if self.route:
        #     self.get_logger().info(f"⚡ 새로운 목적지 [{dest}] 요청 → 현재 작업 중단 후 재시작")
        #     self.route = []
        #     self.current_step = 0
        #     self.door_triggered = False
        #     self.pending_target = None

        # 경로 설정 및 시작
        self.get_logger().info(f"🗺️ 목적지 [{dest}] 경로 설정 시작")
        self.setup_route(dest)

    def door_callback(self, msg: Bool):
        if msg.data and not self.door_triggered:  # 문 열림 신호
            self.door_triggered = True
            self.get_logger().info("🚪 문 열림 신호 수신")
            self.process_next_step()
        elif not msg.data:  # 문 닫힘 신호
            self.door_triggered = False
            self.get_logger().info("🚪 문 닫힘 감지")

            # 2자리 신호 대기 중이면 3초 후 엘리베이터 명령 실행
            if self.waiting_for_elevator:
                self.get_logger().info("⏳ 문 닫힘 감지 - 3초 대기 후 엘리베이터 명령 실행")
                # 기존 타이머가 있으면 취소
                if self.elevator_timer:
                    self.elevator_timer.cancel()
                # 3초 후 엘리베이터 명령 실행하는 타이머 생성
                self.elevator_timer = self.create_timer(3.0, self.execute_elevator_command)
            else:
                self.get_logger().info("🚪 문 닫힘 - 다음 문 열림 대기")

    def setup_route(self, dest):
        if dest == 0:  # 의국은 특별 경로
            self.route = [1, 12, 200]
        else:
            # 일반 호실: [출발층, 출발층+목적층, 목적지호실]
            dest_str = str(dest)
            if len(dest_str) == 3:  # 3자리 호실 (301, 302 등)
                target_floor = int(dest_str[0])  # 목적층 (3층)
                from_floor = 1  # 기본 출발층은 1층

                # 출발층+목적층 계산 (1층에서 3층으로 = 13)
                floor_route = int(f"{from_floor}{target_floor}")

                self.route = [from_floor, floor_route, dest]
                self.get_logger().info(f"🗺️ Route 설정: {from_floor}층 → {target_floor}층 → {dest}호 = {self.route}")
            else:
                self.get_logger().warn(f"지원하지 않는 목적지 형식: {dest}")

        self.current_step = 0
        self.door_triggered = False
        self.process_next_step()

    def process_next_step(self):
        if self.current_step >= len(self.route):
            self.get_logger().info("✅ 목적지 도착 완료!")
            self.arrival_pub.publish(Bool(data=True))
            self.route = []
            self.current_step = 0
            self.door_triggered = False

            if self.pending_target:
                target = self.pending_target
                self.pending_target = None
                self.setup_route(target)

            return

        # 목적지 이동 신호를 퍼블리시
        step_id = self.route[self.current_step]
        self.get_logger().info(f"🚀 Step {step_id} 이동 시작...")
        self.mover_pub.publish(Int32(data=step_id))
        self.last_sent_command = step_id  # 마지막 명령 저장
        self.current_step += 1

    def move_complete_callback(self, msg: Bool):
        """mover에서 이동 완료 신호를 받았을 때"""
        if msg.data:
            step_id = self.last_sent_command if self.last_sent_command else "unknown"
            self.get_logger().info(f"✅ Step {step_id} 이동 완료!")

            # 2자리 route (층간 이동)는 엘리베이터 제어가 완료될 때까지 대기
            if len(str(step_id)) == 2 and str(step_id)[0] != str(step_id)[1]:  # 층간 이동 (11,22,33 제외)
                # 목표 층 계산 (2자리 숫자의 두 번째 자리 - 1)
                target_floor = int(str(step_id)[1]) - 1  # 3층 -> 2, 2층 -> 1
                self.target_floor_data = str(target_floor)
                self.get_logger().info(f"⏳ 층간 이동 route {step_id} 완료 - 문 닫힘 대기 중... (목표층 데이터: {self.target_floor_data})")
                self.waiting_for_elevator = True  # 엘리베이터 대기 상태 설정
                # 다음 스텝은 엘리베이터 명령 완료 후 실행됨
            else:
                # 즉시 다음 스텝으로 진행 (1,2,3, 같은층이동 11,22,33, 및 3자리 route)
                self.process_next_step()

    def execute_elevator_command(self):
        """3초 대기 후 엘리베이터 명령 실행"""
        self.get_logger().info("🚁 엘리베이터 명령 실행")

        # 타이머 정리
        if self.elevator_timer:
            self.elevator_timer.cancel()
            self.elevator_timer = None

        # 목표 층 데이터 확인
        floor_data = self.target_floor_data if self.target_floor_data else "2"

        try:
            # 스크립트 파일로 엘리베이터 명령 실행 (터미널 창 없이)
            script_content = f'''#!/bin/bash
gz topic -p /gazebo/world/elevator -m 'data: "{floor_data}"'
echo "Elevator command executed for floor {floor_data}"
'''

            # 스크립트 파일 생성
            with open('/tmp/elevator_cmd.sh', 'w') as f:
                f.write(script_content)

            # 실행 권한 부여
            subprocess.run(['chmod', '+x', '/tmp/elevator_cmd.sh'])

            # 백그라운드에서 스크립트 실행 (터미널 창 열지 않음)
            result = subprocess.run(['/tmp/elevator_cmd.sh'], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                self.get_logger().info(f"✅ 엘리베이터 명령 실행 성공 (층 데이터: {floor_data})")
                if result.stdout.strip():
                    self.get_logger().info(f"명령 출력: {result.stdout.strip()}")
            else:
                self.get_logger().error(f"❌ 엘리베이터 명령 실패 - stderr: {result.stderr}")

            # 스크립트 파일 정리
            subprocess.run(['rm', '-f', '/tmp/elevator_cmd.sh'])

        except subprocess.TimeoutExpired:
            self.get_logger().error("❌ 엘리베이터 명령 타임아웃 (10초)")
        except Exception as e:
            self.get_logger().error(f"❌ 엘리베이터 명령 실행 중 오류: {e}")

        # 대기 상태 해제 및 다음 스텝으로 진행
        self.waiting_for_elevator = False
        self.get_logger().info("⏰ 엘리베이터 명령 완료! 다음 스텝으로 진행합니다.")
        self.process_next_step()

    def timer_callback_once(self):
        """3초 대기 후 호출되는 일회성 타이머 콜백"""
        self.get_logger().info("⏰ 대기 완료! 다음 스텝으로 진행합니다.")
        self.process_next_step()

def main(args=None):
    rclpy.init(args=args)
    node = TurtlebotMain()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()