#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from gazebo_msgs.msg import ModelState
import math

def create_pose(x, y, z, yaw):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.position.z = z
    pose.pose.orientation.z = math.sin(yaw / 2.0)
    pose.pose.orientation.w = math.cos(yaw / 2.0)
    return pose

def teleport(node, x, y, z, yaw):
    pub = node.create_publisher(ModelState, '/gazebo/set_model_state', 10)
    state = ModelState()
    state.model_name = 'turtlebot3_burger'
    state.pose.position.x = x
    state.pose.position.y = y
    state.pose.position.z = z
    state.pose.orientation.z = math.sin(yaw / 2.0)
    state.pose.orientation.w = math.cos(yaw / 2.0)

    # publisher 연결 대기
    while pub.get_subscription_count() == 0:
        rclpy.spin_once(node, timeout_sec=0.1)

    pub.publish(state)
    print(f"✨ Teleported {state.model_name} to ({x}, {y}, {z})")

def run_course(navigator, node, course_num):
    """코스 실행"""
    if course_num == "1":
        print("코스 1 실행 중...")
        goal1 = create_pose(1.6, 19.0, 1.0, 0.0)
        navigator.goToPose(goal1)
        while not navigator.isTaskComplete():
            rclpy.spin_once(node, timeout_sec=0.1)

        teleport(node, 1.6, 19.0, 7.0, 0.0)

        goal2 = create_pose(1.0, 9.0, 0.0, 0.0)
        navigator.goToPose(goal2)
        while not navigator.isTaskComplete():
            rclpy.spin_once(node, timeout_sec=0.1)

    elif course_num == "2":
        print("코스 2 실행 중...")
        goal1 = create_pose(-1.0, 0.0, 0.0, 0.0)
        navigator.goToPose(goal1)
        while not navigator.isTaskComplete():
            rclpy.spin_once(node, timeout_sec=0.1)

        teleport(node, -2.0, -2.0, 0.5, math.pi/2)

        goal2 = create_pose(-3.0, -3.0, 0.0, 0.0)
        navigator.goToPose(goal2)
        while not navigator.isTaskComplete():
            rclpy.spin_once(node, timeout_sec=0.1)

def main():
    rclpy.init()
    node = rclpy.create_node('multi_course_controller')
    navigator = BasicNavigator()
    print("✅ Nav2 준비 완료!")

    try:
        while True:
            cmd = input("명령어 입력 (1=코스1, 2=코스2, stop=종료): ").strip()
            if cmd == "stop":
                print("🛑 종료합니다.")
                break
            elif cmd in ["1", "2"]:
                run_course(navigator, node, cmd)
            else:
                print("⚠️ 잘못된 명령어입니다. 다시 입력하세요.")

    finally:
        navigator.lifecycleShutdown()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
