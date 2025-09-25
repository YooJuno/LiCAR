#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

class TurtlebotMover(Node):
    def __init__(self):
        super().__init__('turtlebot_mover_node')
        self.navigator = BasicNavigator()

        self.create_subscription(Int32, '/turtlebot_command', self.command_callback, 10)
        self.get_logger().info("✅ Mover node ready")

        self.cases = {
            1:  {"action": "move", "x": -0.15, "y": 2.5},    # 의국
            11: {"action": "move", "x": 1.8, "y": 19.0},     # 엘리베이터 앞
            12: {"action": "move", "x": 1.8, "y": 21.8},    # 엘리베이터 안
            301: {"action": "move", "x": -2.2, "y": -7.3},   # 301호
            302: {"action": "move", "x": 9.0, "y": -7.3},    # 302호
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

    def run_course(self, course_num):
        case = self.cases.get(course_num)
        if not case or case.get('action') != 'move':
            return
        x, y = case['x'], case['y']
        self.get_logger().info(f"🚀 Move to ({x}, {y})")
        goal = self.create_pose(x, y)
        self.navigator.goToPose(goal)

        while not self.navigator.isTaskComplete():
            rclpy.spin_once(self, timeout_sec=0.1)

        result = self.navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            self.get_logger().info("✨ Move complete")
        else:
            self.get_logger().error(f"❌ Move failed: {result}")

    def command_callback(self, msg):
        cmd = msg.data
        if cmd == 0:
            self.navigator.cancelTask()
        else:
            self.run_course(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = TurtlebotMover()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
