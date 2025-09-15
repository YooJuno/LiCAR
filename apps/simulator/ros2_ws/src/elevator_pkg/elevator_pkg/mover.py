#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from gazebo_msgs.srv import SetEntityState
from gazebo_msgs.msg import EntityState
from geometry_msgs.msg import Pose, Point, Quaternion, Twist
from std_srvs.srv import Trigger

FLOOR_Z = {'G': 0.19, '1': 3.19, '2': 6.19}

class ElevatorMoverNode(Node):
    def __init__(self):
        super().__init__('mover_node')
        self.cli = self.create_client(SetEntityState, '/gazebo/set_entity_state')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('waiting /gazebo/set_entity_state...')
        self.model_name = 'car_1'  # 움직일 카 이름
        self.create_service(Trigger, 'go_to_floor_1', self.handle_go_floor_1)
        self.create_service(Trigger, 'go_to_floor_2', self.handle_go_floor_2)

    def move_car(self, z):
        req = SetEntityState.Request()
        state = EntityState()
        state.name = self.model_name
        state.pose = Pose(position=Point(x=0.0, y=19.35, z=z),
                          orientation=Quaternion(x=0, y=0, z=0, w=1))
        state.twist = Twist()
        state.reference_frame = 'world'
        req.state = state
        fut = self.cli.call_async(req)
        rclpy.spin_until_future_complete(self, fut)
        return fut.done() and fut.result() is not None

    def handle_go_floor_1(self, req, res):
        ok = self.move_car(FLOOR_Z['1'])
        res.success = ok
        res.message = 'moved to floor 1' if ok else 'failed'
        return res

    def handle_go_floor_2(self, req, res):
        ok = self.move_car(FLOOR_Z['2'])
        res.success = ok
        res.message = 'moved to floor 2' if ok else 'failed'
        return res

def main(args=None):
    rclpy.init(args=args)
    node = ElevatorMoverNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
