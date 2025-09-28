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
        if self.route:
            self.get_logger().info(f"⚡ 새로운 목적지 [{dest}] 요청 → 현재 작업 중단 후 재시작")
            self.route = []
            self.current_step = 0
            self.door_triggered = False
            self.pending_target = None

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
            self.get_logger().info("🚪 문 닫힘 - 다음 문 열림 대기")

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
        self.get_logger().info(f"🚀 Step {step_id} 이동 시작...")
        self.mover_pub.publish(Int32(data=step_id))
        self.current_step += 1

    def move_complete_callback(self, msg: Bool):
        """mover에서 이동 완료 신호를 받았을 때"""
        if msg.data:
            step_id = self.route[self.current_step - 1] if self.current_step > 0 else "unknown"
            self.get_logger().info(f"✅ Step {step_id} 이동 완료!")

            # 2자리 route (층간 이동)는 엘리베이터 제어가 완료될 때까지 대기
            if len(str(step_id)) == 2 and str(step_id)[0] != str(step_id)[1]:  # 층간 이동 (11,22,33 제외)
                self.get_logger().info(f"⏳ 층간 이동 route {step_id} 완료 - 엘리베이터 제어 완료까지 대기 중...")
                # 다음 스텝은 turtlebot_mover에서 층 이동이 완전히 끝난 후 실행됨
                # process_next_step()을 호출하지 않음 - mover에서 완료 신호를 다시 보낼 때까지 대기
            else:
                # 즉시 다음 스텝으로 진행 (1,2,3, 같은층이동 11,22,33, 및 3자리 route)
                self.process_next_step()

    # def timer_callback_once(self):
    #     """3초 대기 후 호출되는 일회성 타이머 콜백"""
    #     self.get_logger().info("⏰ 대기 완료! 다음 스텝으로 진행합니다.")
    #     self.process_next_step()

def main(args=None):
    rclpy.init(args=args)
    node = TurtlebotMain()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()