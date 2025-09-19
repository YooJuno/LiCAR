#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32, Bool
from geometry_msgs.msg import PoseStamped

class TurtlebotMover(Node):
    def __init__(self):
        super().__init__('turtlebot_mover')

        # 목적지 구독
        self.create_subscription(Int32, '/turtlebot_target', self.target_callback, 10)
        # 엘리베이터 문 상태 구독
        self.create_subscription(Bool, '/elevator/door_state', self.door_callback, 10)

        # Nav2 목표 퍼블리셔
        self.goal_pub = self.create_publisher(PoseStamped, '/goal_pose', 10)

        # 상태 변수
        self.door_triggered = False
        self.route = []
        self.current_step = 0
        self.pending_target = None

        # cases 직접 정의
        self.cases = {
            1:  {"action": "move", "x": -0.15, "y": 2.5},    # 의국
            11: {"action": "move", "x": 5.0, "y": 12.0},     # 엘리베이터 앞
            12: {"action": "move", "x": 4.0, "y": 10.0},     # 엘리베이터 안
            301: {"action": "move", "x": -2.2, "y": -7.3},   # 301호
            302: {"action": "move", "x": 9.0, "y": -7.3},    # 302호
        }

        self.get_logger().info("✅ Main node ready, waiting for target...")

    # 목적지 입력
    def target_callback(self, msg: Int32):
        dest = msg.data
        self.get_logger().info(f"🎯 목적지 요청: {dest}")

        if dest not in self.cases:
            self.get_logger().warn(f"등록되지 않은 목적지: {dest}")
            return

        if self.route:
            self.get_logger().info(f"이동 중 → 요청 저장: {dest}")
            self.pending_target = dest
            return

        self.setup_route(dest)

    # 문 상태 콜백
    def door_callback(self, msg: Bool):
        if msg.data:
            self.door_triggered = True
            self.get_logger().info("🚪 문 열림 신호 수신")
            self.process_next_step()

    # 단계별 route 생성
    def setup_route(self, dest):
        if dest >= 300:  # 병실 → 엘리베이터 경유
            self.route = [11, 12, dest]
        else:
            self.route = [dest]

        self.current_step = 0
        self.door_triggered = False
        self.process_next_step()

    # 단계별 이동 처리
    def process_next_step(self):
        if self.current_step >= len(self.route):
            self.get_logger().info("✅ 목적지 도착 완료!")
            self.route = []
            if self.pending_target:
                target = self.pending_target
                self.pending_target = None
                self.setup_route(target)
            return

        step_id = self.route[self.current_step]
        case = self.cases[step_id]

        # 11번만 문 트리거 없이 이동, 나머지는 모두 트리거 필요
        if step_id != 11:
            if not self.door_triggered:
                self.get_logger().info(f"문 신호 대기 → step {step_id}")
                return
            else:
                self.door_triggered = False  # 신호 사용 후 초기화

        self.send_goal(step_id, case["x"], case["y"])
        self.current_step += 1
        self.process_next_step()

    # Nav2 goal 퍼블리시
    def send_goal(self, step_id, x, y):
        goal_msg = PoseStamped()
        goal_msg.header.frame_id = "map"
        goal_msg.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.position.x = x
        goal_msg.pose.position.y = y
        goal_msg.pose.orientation.w = 1.0

        self.goal_pub.publish(goal_msg)
        self.get_logger().info(f"🚀 Step {step_id} → ({x}, {y}) 이동 시작")

def main(args=None):
    rclpy.init(args=args)
    node = TurtlebotMover()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
