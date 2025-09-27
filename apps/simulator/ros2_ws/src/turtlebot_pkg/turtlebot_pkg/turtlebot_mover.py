#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32, Bool
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

class TurtlebotMover(Node):
    def __init__(self):
        super().__init__('turtlebot_mover_node')
        self.navigator = BasicNavigator()

        self.create_subscription(Int32, '/turtlebot_command', self.command_callback, 10)
        self.completion_pub = self.create_publisher(Bool, '/turtlebot/move_complete', 10)
        
        self.get_logger().info("✅ Mover node ready")

        self.waypoints = {
            1:  {"x": -0.15, "y": 2.5},
            11: {"x": 1.8, "y": 20.0},
            12: {"x": 1.8, "y": 21.7}, 
            301: {"x": -2.2, "y": -7.3},
            302: {"x": 9.0, "y": -7.3},
        }

    def command_callback(self, msg: Int32):
        cmd = msg.data
        if cmd == 0:
            self.get_logger().info('Canceling current task...')
            self.navigator.cancelTask()
            return
        
        waypoint = self.waypoints.get(cmd)
        if not waypoint:
            self.get_logger().error(f"알 수 없는 명령: {cmd}")
            return

        x, y = waypoint['x'], waypoint['y']
        self.get_logger().info(f"🚀 {cmd}번 지점 ({x}, {y})으로 이동을 시작합니다.")
        
        goal_pose = self.create_pose(x, y)
        
        nav_future = self.navigator.goToPose(goal_pose)
        nav_future.add_done_callback(self.goal_done_callback)

    # [수정] future 인자를 받도록 변경
    def goal_done_callback(self, future):
        result = self.navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            self.get_logger().info("✨ Move complete")
            completion_msg = Bool()
            completion_msg.data = True
            self.completion_pub.publish(completion_msg)
        elif result == TaskResult.CANCELED:
            self.get_logger().warn("⚠️ Goal was canceled!")
        elif result == TaskResult.FAILED:
            self.get_logger().error("❌ Goal failed!")
        else:
            self.get_logger().error(f"❓ Move failed with unknown result: {result}")

    def create_pose(self, x, y, yaw=0.0):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.orientation.z = math.sin(yaw/2)
        pose.pose.orientation.w = math.cos(yaw/2)
        return pose

def main(args=None):
    rclpy.init(args=args)
    node = TurtlebotMover()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()