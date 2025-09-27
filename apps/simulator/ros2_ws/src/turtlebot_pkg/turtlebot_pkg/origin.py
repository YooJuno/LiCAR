#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32, Bool, String

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

        self.get_logger().info("✅ Main node ready, waiting for target...")

    def target_callback(self, msg: Int32):
        dest = msg.data
        self.get_logger().info(f"🎯 목적지 요청: {dest}")

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

        # 목적지가 이미 이동 중이면 대기
        if self.route:
            self.get_logger().info(f"이동 중 → 요청 저장: {dest}")
            self.pending_target = dest
            return

        # 0번(의국), 301번, 302번은 모두 엘리베이터를 경유해야 함
        self.setup_route(dest)

    def door_callback(self, msg: Bool):
        if msg.data and not self.door_triggered:  # 문 열림 신호
            self.door_triggered = True
            self.get_logger().info("🚪 문 열림 신호 수신")
            self.process_next_step()
        elif not msg.data:  # 문 닫힘 신호
            self.door_triggered = False
            self.get_logger().info("🚪 문 닫힘 - 다음 문 열림 대기")

        # else:  # 문 닫힘
        #     if self.door_open:  # 직전에 열렸었음 → 이제 닫힘 감지
        #         self.door_open = False
        #         self.get_logger().info("🚪 문 닫힘 감지 → 엘리베이터 3층 이동 명령 전송")
        #         self.elevator_pub.publish(String(data="2"))

    def setup_route(self, dest):
        if dest == 0:  # 의국은 특별 경로
            self.route = [1, 12, 200]
        else:
            # 일반 호실: [출발층, 출발층+목적층, 목적지호실]
            dest_str = str(dest)
            if len(dest_str) == 3:  # 3자리 호실 (301, 302 등)
                target_floor = int(dest_str[0])  # 목적층 (3층)
                from_floor = 2  # 기본 출발층은 2층

                # 출발층+목적층 계산 (2층에서 3층으로 = 23)
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
        self.get_logger().info(f"🚀 Step {step_id} 으로 이동 시작")
        self.mover_pub.publish(Int32(data=step_id))
        self.current_step += 1

    def move_complete_callback(self, msg: Bool):
        """mover에서 이동 완료 신호를 받았을 때"""
        if msg.data:
            self.get_logger().info("✅ 이동 완료 신호 수신")
            # 다음 스텝으로 진행
            self.process_next_step()

def main(args=None):
    rclpy.init(args=args)
    node = TurtlebotMain()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
