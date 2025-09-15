#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from gazebo_msgs.srv import SpawnEntity, DeleteEntity
from geometry_msgs.msg import Pose, Point, Quaternion
from std_srvs.srv import Trigger
import os

BASE = os.path.expanduser('~/aws-robomaker-hospital-world/models')
MODEL_PATHS = {
    'portal': os.path.join(BASE, 'aws_robomaker_hospital_elevator_01_portal', 'model.sdf'),
    'car'   : os.path.join(BASE, 'aws_robomaker_hospital_elevator_01_car', 'model.sdf'),
    'door'  : os.path.join(BASE, 'aws_robomaker_hospital_elevator_01_door', 'model.sdf'),
}

ENTITIES = [
    ('portal_1', 'portal', (-1.50654, 19.4813, 0.19)),
    ('portal_2', 'portal', (1.51134, 19.4870, 0.19)),
    ('car_1',    'car',    (-1.49587, 19.35,   0.19)),
    ('car_2',    'car',    (1.5407,   19.35,   0.19)),
    ('door_1',   'door',   (-1.51,    19.35,   0.19)),
    ('door_2',   'door',   (1.52843,  19.3627, 0.19)),
]

class ElevatorSpawnerNode(Node):
    def __init__(self):
        super().__init__('spawner_node')

        self.spawn_cli = self.create_client(SpawnEntity, '/spawn_entity')
        self.delete_cli = self.create_client(DeleteEntity, '/delete_entity')

        while not self.spawn_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('waiting /spawn_entity...')
        while not self.delete_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('waiting /delete_entity...')

        self.create_service(Trigger, 'spawn_all', self.handle_spawn_all)
        self.create_service(Trigger, 'despawn_all', self.handle_despawn_all)

    def read_model(self, path):
        with open(path, 'r') as f:
            xml = f.read()
        xml = xml.replace('<static>1</static>', '<static>0</static>')
        xml = xml.replace('<static>true</static>', '<static>false</static>')
        return xml

    def spawn_entity(self, name, model_key, pos):
        xml = self.read_model(MODEL_PATHS[model_key])
        req = SpawnEntity.Request()
        req.name = name
        req.xml = xml
        req.robot_namespace = ''
        x, y, z = pos
        req.initial_pose = Pose(position=Point(x=x, y=y, z=z),
                                orientation=Quaternion(x=0, y=0, z=0, w=1))
        req.reference_frame = 'world'
        fut = self.spawn_cli.call_async(req)
        rclpy.spin_until_future_complete(self, fut)
        return fut.done() and fut.result() is not None

    def delete_entity(self, name):
        req = DeleteEntity.Request()
        req.name = name
        fut = self.delete_cli.call_async(req)
        rclpy.spin_until_future_complete(self, fut)
        return fut.done() and fut.result() is not None

    def handle_spawn_all(self, req, res):
        ok = all(self.spawn_entity(n, k, p) for n, k, p in ENTITIES)
        res.success = ok
        res.message = 'spawned all' if ok else 'some failed'
        return res

    def handle_despawn_all(self, req, res):
        ok = all(self.delete_entity(n) for n, _, _ in ENTITIES)
        res.success = ok
        res.message = 'deleted all' if ok else 'some failed'
        return res

def main(args=None):
    rclpy.init(args=args)
    node = ElevatorSpawnerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
