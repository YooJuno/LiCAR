#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from elevator_interfaces.action import MoveElevator
import time


class ElevatorMover(Node):
    def __init__(self):
        super().__init__('elevator_controller_node')

        # JointTrajectory 퍼블리셔
        self.traj_pub = self.create_publisher(JointTrajectory, '/set_joint_trajectory', 10)

        # 액션 서버
        self._action_server = ActionServer(
            self,
            MoveElevator,
            'move_elevator',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )

        # 현재 엘리베이터 위치 (실제라면 /joint_states 구독으로 업데이트해야 정확)
        self.current_z = 0.19

    def goal_callback(self, goal_request):
        self.get_logger().info(f"Received goal request: target_z={goal_request.target_z:.2f}")
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info("Received cancel request")
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        target_z = goal_handle.request.target_z
        self.get_logger().info(f"Executing goal: move elevator to {target_z:.2f} m")

        feedback_msg = MoveElevator.Feedback()

        step = 0.01 if target_z > self.current_z else -0.01

        while abs(target_z - self.current_z) > 1e-3:
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().warn("Goal canceled")
                return MoveElevator.Result(success=False)

            # 위치 업데이트
            self.current_z += step

            # JointTrajectory 메시지 구성
            traj = JointTrajectory()
            traj.header.frame_id = 'base_link'
            traj.joint_names = ['lift_joint']
            point = JointTrajectoryPoint()
            point.positions = [self.current_z]
            point.time_from_start.sec = 0
            point.time_from_start.nanosec = 50000000
            traj.points = [point]

            self.traj_pub.publish(traj)

            # 피드백 전송
            feedback_msg.current_z = self.current_z
            goal_handle.publish_feedback(feedback_msg)

            # 속도 제어 (50ms 간격 이동)
            time.sleep(0.05)

        goal_handle.succeed()
        self.get_logger().info(f"Reached target z={target_z:.2f} m")

        result = MoveElevator.Result()
        result.success = True
        return result


def main(args=None):
    rclpy.init(args=args)
    node = ElevatorMover()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
