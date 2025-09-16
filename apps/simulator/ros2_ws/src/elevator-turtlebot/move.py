#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from gazebo_msgs.srv import SetModelState
from gazebo_msgs.msg import ModelState
import time

class ElevatorMover(Node):
    def __init__(self):
        super().__init__('elevator_mover')
        self.cli = self.create_client(SetModelState, '/gazebo/set_model_state')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /gazebo/set_model_state service...')

    def move_to_z_smooth(self, model_name: str, z_start: float, z_end: float, step: float=0.1, delay: float=0.1):
        z = z_start
        while z <= z_end:
            msg = ModelState()
            msg.model_name = model_name
            msg.pose.position.x = -1.49587  # 스폰 위치 기준 x
            msg.pose.position.y = 19.35     # 스폰 위치 기준 y
            msg.pose.position.z = z
            msg.pose.orientation.x = 0.0
            msg.pose.orientation.y = 0.0
            msg.pose.orientation.z = 0.0
            msg.pose.orientation.w = 1.0
            msg.twist.linear.x = 0.0
            msg.twist.linear.y = 0.0
            msg.twist.linear.z = 0.0
            msg.twist.angular.x = 0.0
            msg.twist.angular.y = 0.0
            msg.twist.angular.z = 0.0
            msg.reference_frame = 'world'

            req = SetModelState.Request()
            req.model_state = msg

            future = self.cli.call_async(req)
            rclpy.spin_until_future_complete(self, future)

            if future.result():
                self.get_logger().info(f'{model_name} z={z:.2f}')
            else:
                self.get_logger().error('Failed to move model')

            z += step
            time.sleep(delay)

def main(args=None):
    rclpy.init(args=args)
    mover = ElevatorMover()

    mover.move_to_z_smooth('car_1', z_start=0.18, z_end=3.0, step=0.05, delay=0.05)

    mover.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
