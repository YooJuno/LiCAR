#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
from turtlebot_pkg.turtlebot_mover import TurtlebotMover

class MainController(Node):
    def __init__(self):
        super().__init__('main_node')

        # 목적지 입력 구독
        self.dest_sub = self.create_subscription(
            Int32, 'turtlebot_target', self.target_callback, 10)

        # 엘리베이터 문 상태 구독 (0=닫힘,1=열림)
        self.elevator_joint_sub = self.create_subscription(
            Int32, 'elevator_door_state', self.elevator_joint_callback, 10)

        # mover 객체 생성 (로그 + Nav2 대기 포함)
        self.mover = TurtlebotMover()

        # 상태
        self.door_open_signal = False
        self.current_target = None
        self.sequence = []
        self.step_idx = 0

        self.get_logger().info("✅ Main node ready, waiting for target...")

    # 목적지 입력
    def target_callback(self, msg):
        if self.current_target is None:
            self.current_target = msg.data
            self.get_logger().info(f"🎯 Target received: {self.current_target}")

            # 층 신경 안쓰고 항상 11 → 12 → 목적지
            self.sequence = [11, 12, self.current_target]
            self.step_idx = 0

    # 문 열림 신호
    def elevator_joint_callback(self, msg):
        if msg.data == 1 and not self.door_open_signal:
            self.door_open_signal = True

    # 단계별 이동 + Nav2 완료 대기 + 로그
    def send_move_and_wait(self, case_num):
        self.get_logger().info(f"📍 Moving to case {case_num}...")
        self.mover.run_course(case_num)  # 내부에서 로그 + 완료 대기

    # main loop
    def run(self):
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)
            if self.current_target is None or self.step_idx >= len(self.sequence):
                continue

            current_case = self.sequence[self.step_idx]

            # 12와 목적지는 문 열림 확인
            if current_case in [12, self.current_target]:
                if not self.door_open_signal:
                    continue  # 문 열림 대기
                self.door_open_signal = False  # 한 번만 인식

            # 이동
            self.send_move_and_wait(current_case)
            self.step_idx += 1

            # 목적지 도착 후 초기화
            if self.step_idx == len(self.sequence):
                self.get_logger().info(f"🏁 Reached final destination {self.current_target}")
                self.current_target = None
                self.sequence = []
                self.step_idx = 0

def main(args=None):
    rclpy.init(args=args)
    node = MainController()
    try:
        node.run()
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
