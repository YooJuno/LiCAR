#!/usr/bin/env python3
import os, yaml, math, rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
from gazebo_msgs.srv import SpawnEntity, DeleteEntity, GetEntityState

class TurtlebotSpawner(Node):
    def __init__(self):
        super().__init__('turtlebot_spawner_node')

        self.spawn_cli = self.create_client(SpawnEntity, '/spawn_entity')
        self.delete_cli = self.create_client(DeleteEntity, '/delete_entity')
        self.get_state_cli = self.create_client(GetEntityState, '/get_entity_state')

        yaml_path = os.path.expanduser('~/ros2_ws/src/turtlebot_pkg/config/cases.yaml')
        with open(yaml_path, 'r') as f:
            self.cases = yaml.safe_load(f)['cases']

        sdf_file = os.path.expanduser('~/turtle_ws/src/turtlebot3_simulations/turtlebot3_gazebo/models/turtlebot3_burger/model.sdf')
        with open(sdf_file, 'r') as f:
            self.sdf_content = f.read()

        self.create_subscription(Int32, 'turtlebot_command', self.command_callback, 10)
        self.get_logger().info("✅ Spawner node ready")

    def entity_exists(self, name='turtlebot3_burger'):
        if not self.get_state_cli.wait_for_service(timeout_sec=2.0):
            return False
        req = GetEntityState.Request()
        req.name = name
        future = self.get_state_cli.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=1.0)
        try:
            future.result()
            return True
        except Exception:
            return False

    def spawn_robot(self, x=0.0, y=0.0, z=0.1, yaw=0.0):
        if not self.spawn_cli.wait_for_service(timeout_sec=5.0):
            return
        req = SpawnEntity.Request()
        req.name = 'turtlebot3_burger'
        req.xml = self.sdf_content
        req.initial_pose.position.x = x
        req.initial_pose.position.y = y
        req.initial_pose.position.z = z
        req.initial_pose.orientation.z = math.sin(yaw/2)
        req.initial_pose.orientation.w = math.cos(yaw/2)
        future = self.spawn_cli.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        self.get_logger().info("✨ Spawn complete")

    def despawn_robot(self):
        if not self.entity_exists():
            self.get_logger().warn("⚠️ Robot does not exist")
            return
        if not self.delete_cli.wait_for_service(timeout_sec=5.0):
            return
        req = DeleteEntity.Request()
        req.name = 'turtlebot3_burger'
        future = self.delete_cli.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=3.0)
        self.get_logger().info("🗑️ Despawn complete")

    def run_course(self, course_num):
        case = self.cases.get(course_num)
        if not case:
            return
        action = case.get('action')
        if action == 'spawn':
            self.spawn_robot(case.get('x',0), case.get('y',0), case.get('z',0.1), case.get('yaw',0.0))
        elif action == 'despawn':
            self.despawn_robot()

    def command_callback(self, msg):
        self.run_course(msg.data)

def main():
    rclpy.init()
    node = TurtlebotSpawner()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
