#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32

class MainController(Node):
    def __init__(self):
        super().__init__('main_node')

        # mover에게 명령 발행
        self.cmd_pub = self.create_publisher(Int32, 'turtlebot_command', 10)

        # 엘리베이터 문 joint 상태 구독 (0=닫힘, 1=열림)
        self.elevator_joint_sub = self.create_subscription(
            Int32, 'elevator_door_state', self.elevator_joint_callback, 10)

        self.door_open_signal = False
        self.step = 0  # 진행 단계 관리

        self.get_logger().info("✅ Main node ready")

    def elevator_joint_callback(self, msg):
        if msg.data == 1:  # 문 열림 신호
            self.door_open_signal = True

    def send_move_command(self, case_num):
        self.cmd_pub.publish(Int32(data=case_num))
        self.get_logger().info(f"📍 Mover command sent: {case_num}")

    def move_to_destination(self, dest_code):
        # 단계별 이동: 1 → 11 → 12 → 목적지
        sequence = [11, 12, dest_code]

        for idx, case in enumerate(sequence):
            self.get_logger().info(f"➡️ Moving step {idx+1}: case {case}")

            if case in [12, dest_code]:
                # 문 열림 대기
                self.door_open_signal = False
                self.get_logger().info("⏳ Waiting for elevator door to open")
                while not self.door_open_signal:
                    rclpy.spin_once(self, timeout_sec=0.1)

            self.send_move_command(case)


def main(args=None):
    rclpy.init(args=args)
    node = MainController()

    # 테스트 예시: 301 목적지로 이동
    node.move_to_destination(301)

    rclpy.shutdown()


if __name__ == "__main__":
    main()
