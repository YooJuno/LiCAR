#!/usr/bin/env python3
import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

def main():
    rclpy.init()
    
    navigator = BasicNavigator()
    
    # Nav2 준비 대기
    navigator.waitUntilNav2Active()

    # 목표 위치 설정
    goal_pose = PoseStamped()
    goal_pose.header.frame_id = 'map'
    goal_pose.pose.position.x = 1.6
    goal_pose.pose.position.y = 19.0
    goal_pose.pose.orientation.w = 1.0

    print("Moving to goal...")
    navigator.goToPose(goal_pose)

    # 이동 완료 대기
    while not navigator.isTaskComplete():
        feedback = navigator.getFeedback()
        if feedback is not None:
            print(f"Distance remaining: {feedback.distance_remaining:.2f} m")

    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        print("Goal reached successfully!")
    else:
        print(f"Goal failed with result code: {result}")

    rclpy.shutdown()

if __name__ == '__main__':
    main()
