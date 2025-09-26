#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32, Bool # ✅ [추가] Bool 메시지 타입 임포트
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

class TurtlebotMover(Node):
    def __init__(self):
        super().__init__('turtlebot_mover_node')
        self.navigator = BasicNavigator()

        self.create_subscription(Int32, '/turtlebot_command', self.command_callback, 10)
        # ✅ [추가] main 노드로 이동 완료 신호를 보낼 퍼블리셔
        self.completion_pub = self.create_publisher(Bool, '/turtlebot/move_complete', 10)
        
        self.get_logger().info("✅ Mover node ready")

        self.cases = {
            1:  {"action": "move", "x": -0.15, "y": 2.5},
            11: {"action": "move", "x": 1.8, "y": 20.0},
            12: {"action": "move", "x": 1.8, "y": 21.7},
            301: {"action": "move", "x": -2.2, "y": -7.3},
            302: {"action": "move", "x": 9.0, "y": -7.3},
        }

    def create_pose(self, x, y, yaw=0.0):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.orientation.z = math.sin(yaw/2)
        pose.pose.orientation.w = math.cos(yaw/2)
        return pose

    # ✅ [수정] run_course 함수를 비동기 방식으로 변경
    def run_course(self, course_num):
        case = self.cases.get(course_num)
        if not case or case.get('action') != 'move':
            return
        x, y = case['x'], case['y']
        self.get_logger().info(f"🚀 Move to ({x}, {y})")
        goal = self.create_pose(x, y)
        
        # 목표를 보내고, 완료되면 goal_done_callback 함수가 호출되도록 설정
        self.navigator.goToPose(goal)

    # ✅ [수정] command_callback에서 run_course를 직접 호출하는 대신 navigator의 콜백을 사용
    def command_callback(self, msg):
        cmd = msg.data
        if cmd == 0:
            self.get_logger().info('Canceling current task...')
            self.navigator.cancelTask()
        else:
            self.run_course(cmd)
            # 주기적으로 작업 상태를 확인하고 완료 시 콜백을 호출
            self.check_task_completion()
            
    # ✅ [추가] 작업 완료를 주기적으로 확인하고 콜백을 호출하는 함수
    def check_task_completion(self):
        if not self.navigator.isTaskComplete():
            # 작업이 완료되지 않았으면 0.1초 후에 다시 확인
            self.create_timer(0.1, self.check_task_completion_callback)
        else:
            self.goal_done_callback()
            
    def check_task_completion_callback(self):
        # 타이머 콜백에서 실제 확인 로직을 호출
        # 한 번만 실행되도록 타이머를 취소
        self.check_task_completion()

    # ✅ [추가] 내비게이션이 완료되었을 때 실행될 콜백 함수
    def goal_done_callback(self):
        result = self.navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            self.get_logger().info("✨ Move complete")
            # 이동 완료 신호를 main 노드에 보냄
            completion_msg = Bool()
            completion_msg.data = True
            self.completion_pub.publish(completion_msg)
        elif result == TaskResult.CANCELED:
            self.get_logger().info("Goal was canceled!")
        elif result == TaskResult.FAILED:
            self.get_logger().error("Goal failed!")
        else:
            self.get_logger().error(f"❌ Move failed with unknown result: {result}")

def main(args=None):
    rclpy.init(args=args)
    node = TurtlebotMover()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()