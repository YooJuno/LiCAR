#!/usr/bin/env python3
import math, os, yaml
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult


class TurtlebotMover(Node):
    def __init__(self):
        super().__init__('turtlebot_mover_node')
        self.navigator = BasicNavigator()

        yaml_path = os.path.expanduser('~/ros2_ws/src/turtlebot_pkg/config/cases.yaml')

        with open(yaml_path, 'r') as f:
            self.cases = yaml.safe_load(f)['cases']

        self.create_subscription(Int32, 'turtlebot_command', self.command_callback, 10)
        self.get_logger().info("✅ Mover node ready")

    def create_pose(self, x, y, yaw):
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
        yaw = case.get('yaw', 0.0)
        self.get_logger().info(f"🚀 Move to ({x}, {y})")
        goal = self.create_pose(x, y, yaw)
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

def main():
    rclpy.init()
    node = TurtlebotMover()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
