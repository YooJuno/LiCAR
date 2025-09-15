#!/usr/bin/env python3
import os
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose, Point, Quaternion
from gazebo_msgs.srv import SpawnEntity

class ElevatorSpawner(Node):
    def __init__(self):
        super().__init__('spawner_node')

        HOME = os.environ.get('HOME', '')
        self.declare_parameter('entity_name', 'car_1')
        self.declare_parameter('file_path',
            os.path.join(HOME, 'aws-robomaker-hospital-world', 'models', 'licar_elevator', 'model.sdf'))
        self.declare_parameter('x', -1.49587)
        self.declare_parameter('y', 19.35)
        self.declare_parameter('z', 0.19)
        self.declare_parameter('qx', 0.0)
        self.declare_parameter('qy', 0.0)
        self.declare_parameter('qz', 0.0)
        self.declare_parameter('qw', 1.0)
        self.declare_parameter('reference_frame', 'world')

        self.entity_name = self.get_parameter('entity_name').get_parameter_value().string_value
        self.file_path   = self.get_parameter('file_path').get_parameter_value().string_value
        self.x           = float(self.get_parameter('x').value)
        self.y           = float(self.get_parameter('y').value)
        self.z           = float(self.get_parameter('z').value)
        self.qx          = float(self.get_parameter('qx').value)
        self.qy          = float(self.get_parameter('qy').value)
        self.qz          = float(self.get_parameter('qz').value)
        self.qw          = float(self.get_parameter('qw').value)
        self.reference_frame = self.get_parameter('reference_frame').get_parameter_value().string_value

        self.cli = self.create_client(SpawnEntity, '/spawn_entity')
        self.get_logger().info('waiting for /spawn_entity ...')
        self.cli.wait_for_service()

        self.timer = self.create_timer(0.1, self._once)

    def _once(self):
        self.timer.cancel()
        if not os.path.isfile(self.file_path):
            self.get_logger().error(f'file not found: {self.file_path}')
            return

        with open(self.file_path, 'r') as f:
            xml = f.read().strip()

        if not xml:
            self.get_logger().error('model.sdf is empty (read 0 bytes)')
            return

        if '<model' not in xml:
            self.get_logger().error('model.sdf does not contain <model> element')
            return

        req = SpawnEntity.Request()
        req.name = self.entity_name
        req.xml = xml
        req.robot_namespace = ''
        p = Pose()
        p.position = Point(x=self.x, y=self.y, z=self.z)
        p.orientation = Quaternion(x=self.qx, y=self.qy, z=self.qz, w=self.qw)
        req.initial_pose = p
        req.reference_frame = self.reference_frame

        self.get_logger().info(
            f"Spawning '{self.entity_name}' from file at "
            f"({self.x:.3f},{self.y:.3f},{self.z:.3f})"
        )
        fut = self.cli.call_async(req)
        rclpy.spin_until_future_complete(self, fut, timeout_sec=15.0)
        if not fut.done() or fut.result() is None:
            self.get_logger().error('spawn service timeout (file path)')
            return

        resp = fut.result()
        # gazebo_ros 하위 버전은 success/status_message 필드가 없을 수도 있어 방어적 처리
        ok = getattr(resp, 'success', True)
        msg = getattr(resp, 'status_message', '')
        if not ok:
            self.get_logger().error(f"spawn failed: {msg}")
            return

        self.get_logger().info(f"Spawned '{self.entity_name}' OK. {msg if msg else ''}")

def main(args=None):
    rclpy.init(args=args)
    node = ElevatorSpawner()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
