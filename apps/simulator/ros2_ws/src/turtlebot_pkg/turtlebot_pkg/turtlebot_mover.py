#!/usr/bin/env python3
import math
import subprocess
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
        self.create_subscription(Bool, '/elevator/door_state', self.door_state_callback, 10)
        # 엘리베이터 층 정보 구독 (층 변경 감지용)
        self.create_subscription(Int32, '/elevator/current_floor', self.elevator_floor_callback, 10)
        self.completion_pub = self.create_publisher(Bool, '/turtlebot/move_complete', 10)

        # ⭐ 네비게이션 상태와 타이머를 관리할 변수 추가
        self.is_navigating = False
        self.nav_timer = None
        self.current_route = None
        self.just_completed_floor_change = False  # 층간 이동 완료 대기 (11,22,33 제외한 2자리)
        self.just_completed_elevator_boarding = False  # 엘리베이터 탑승 완료 대기 (1,2,3)
        self.door_was_open = False
        self.current_door_state = False  # 현재 문 상태 저장
        self.elevator_command_sent = False  # 엘리베이터 명령 전송 여부
        self.elevator_moving = False  # 엘리베이터 이동 중 여부
        self.current_floor = 2  # 현재 층 (기본값 2층)
        self.target_floor = None  # 목표 층
        
        self.get_logger().info("✅ Mover node ready")

        # 현재 위치 저장용
        self.current_position = None

        self.waypoints = {
            1: {"x": 1.8, "y": 19.0},   # 1층 엘리베이터 탑승
            2: {"x": 1.8, "y": 19.0},   # 2층 엘리베이터 탑승
            3: {"x": 1.8, "y": 19.0},   # 3층 엘리베이터 탑승
            11: {"x": -0.15, "y": 2.5}, # 1층에서 1층 (간호사실)
            12: {"x": 1.8, "y": 21.8},  # 1층에서 2층
            13: {"x": 1.8, "y": 21.8},  # 1층에서 3층
            21: {"x": 1.8, "y": 21.8},  # 2층에서 1층
            22: {"x": -0.15, "y": 2.5}, # 2층에서 2층 (간호사실)
            23: {"x": 1.8, "y": 21.8},  # 2층에서 3층
            31: {"x": 1.8, "y": 21.8},  # 3층에서 1층
            32: {"x": 1.8, "y": 21.8},  # 3층에서 2층
            33: {"x": -0.15, "y": 2.5}, # 3층에서 3층 (간호사실)
            101: {"x": -2.2, "y": -7.3}, # 1층 01호 (301과 같은 위치)
            102: {"x": 9.0, "y": -7.3},  # 1층 02호 (302와 같은 위치)
            200: {"x": -0.15, "y": 2.5}, # 의국
            201: {"x": -2.2, "y": -7.3}, # 2층 01호 (301과 같은 위치)
            202: {"x": 9.0, "y": -7.3},  # 2층 02호 (302와 같은 위치)
            301: {"x": -2.2, "y": -7.3}, # 3층 01호
            302: {"x": 9.0, "y": -7.3},  # 3층 02호
        }

    def command_callback(self, msg: Int32):
        # 이미 이동 중인 경우, 기존 작업을 취소합니다.
        if self.is_navigating:
            self.get_logger().info('Canceling previous task to start a new one...')
            self.navigator.cancelTask()
            if self.nav_timer:
                self.nav_timer.cancel()
        
        cmd = msg.data
        if cmd == 0:
            self.get_logger().info('Canceling current task...')
            self.navigator.cancelTask()
            self.is_navigating = False
            if self.nav_timer:
                self.nav_timer.cancel()
            return

        # 현재 라우트 저장
        self.current_route = cmd

        waypoint = self.waypoints.get(cmd)
        if not waypoint:
            self.get_logger().error(f"알 수 없는 명령: {cmd}")
            return

        x, y = waypoint['x'], waypoint['y']
        self.get_logger().info(f"🚀 {cmd}번 지점 ({x}, {y})으로 이동을 시작합니다.")

        goal_pose = self.create_pose(x, y)

        # goToPose는 명령 전달 성공 여부를 bool로 반환합니다.
        # 더 이상 future 객체를 사용하지 않습니다.
        self.navigator.goToPose(goal_pose)

        self.is_navigating = True
        # 1초마다 check_nav_status 함수를 호출하는 타이머를 시작합니다.
        self.nav_timer = self.create_timer(1.0, self.check_nav_status)
    
    def check_nav_status(self):
        if not self.is_navigating:
            return

        # isTaskComplete()로 네비게이션 완료 여부를 확인합니다.
        if self.navigator.isTaskComplete():
            # 작업이 완료되면 타이머를 멈춥니다.
            if self.nav_timer:
                self.nav_timer.cancel()
            self.is_navigating = False

            result = self.navigator.getResult()
            if result == TaskResult.SUCCEEDED:
                self.get_logger().info("✨ Move complete")

                # 2자리 route 처리
                if len(str(self.current_route)) == 2:
                    route_str = str(self.current_route)
                    from_floor = int(route_str[0])  # 출발층
                    to_floor = int(route_str[1])    # 목적지층

                    # 같은 층 내 이동 (11, 22, 33)
                    if from_floor == to_floor:
                        self.get_logger().info(f"📍 Route {self.current_route} 완료 - 같은 층 내 이동, 바로 3자리 신호 실행 가능")
                        completion_msg = Bool()
                        completion_msg.data = True
                        self.completion_pub.publish(completion_msg)
                    else:
                        # 층간 이동: 엘리베이터 이용 (11,22,33 제외한 2자리)
                        self.target_floor = to_floor - 1  # data는 층-1
                        self.just_completed_floor_change = True
                        self.get_logger().info(f"📍 Route {self.current_route} 위치 도착 - {from_floor}층에서 {to_floor}층(data:{self.target_floor})으로 이동 후 완료")

                        # 도착 시 문이 이미 닫혀있다면 즉시 엘리베이터 명령 전송
                        if not self.current_door_state:
                            self.get_logger().info("🚪 문이 이미 닫힘 상태, 즉시 엘리베이터 명령 전송")
                            self.send_elevator_command()
                        else:
                            self.get_logger().info("🚪 문이 완전히 닫힐 때까지 대기...")
                        # 층간 이동 route는 목표 층 도착 후 문이 열릴 때 완료 처리
                elif self.current_route in [1, 2, 3]:
                    # 1, 2, 3: 엘리베이터 탑승 신호 (문이 열리면 완료)
                    if self.current_door_state:
                        completion_msg = Bool()
                        completion_msg.data = True
                        self.completion_pub.publish(completion_msg)
                        self.get_logger().info(f"✅ Route {self.current_route} 목표 완료 (문 열림 상태)")
                    else:
                        self.get_logger().info(f"📍 Route {self.current_route} 위치 도착 - 문이 열릴 때까지 대기...")
                        self.just_completed_elevator_boarding = True
                else:
                    # 3자리: 같은 층 내 방 이동, 즉시 완료
                    completion_msg = Bool()
                    completion_msg.data = True
                    self.completion_pub.publish(completion_msg)
                    self.get_logger().info(f"✅ Route {self.current_route} 목표 완료 (같은 층 내 이동)")
            elif result == TaskResult.CANCELED:
                self.get_logger().warn("⚠️ Goal was canceled!")
            elif result == TaskResult.FAILED:
                self.get_logger().error("❌ Goal failed!")
            else:
                self.get_logger().error(f"❓ Move failed with unknown result: {result}")

    def door_state_callback(self, msg: Bool):
        """엘리베이터 문 상태 콜백"""
        door_open = msg.data
        prev_door_state = self.current_door_state
        self.current_door_state = door_open

        # 문이 열린 상태로 변했을 때
        if door_open and not prev_door_state:
            self.door_was_open = True
            self.get_logger().info("🚪 엘리베이터 문 열림 감지")

            # 엘리베이터 탑승 대기 중인 경우 (1, 2, 3) 즉시 완료 처리
            if self.just_completed_elevator_boarding:
                completion_msg = Bool()
                completion_msg.data = True
                self.completion_pub.publish(completion_msg)
                self.get_logger().info(f"✅ Route {self.current_route} 목표 완료 (문 열림 감지)")
                self.just_completed_elevator_boarding = False

            # 층간 이동에서 엘리베이터 명령 전송 후 실제로 목표 층에 도착하고 문이 열리면 완료
            if self.just_completed_floor_change and self.elevator_command_sent and self.current_floor == self.target_floor:
                current_pos = self.get_current_position()
                if current_pos and current_pos[1] >= 20.6:
                    completion_msg = Bool()
                    completion_msg.data = True
                    self.completion_pub.publish(completion_msg)
                    self.get_logger().info(f"✅ Route {self.current_route} 목표 완료 ({self.target_floor}층 실제 도착 후 문 열림)")
                    self.just_completed_floor_change = False
                    self.elevator_command_sent = False
                    self.elevator_moving = False
                    self.target_floor = None

        # 문이 닫힌 상태로 변했을 때 (층간 이동 완료 후에만)
        elif not door_open and prev_door_state and self.just_completed_floor_change:
            self.get_logger().info(f"🚪 엘리베이터 문 완전히 닫힘 감지 - {self.target_floor}층으로 이동 명령 전송")
            self.send_elevator_command()

    def elevator_floor_callback(self, msg: Int32):
        """엘리베이터 현재 층 정보 콜백"""
        prev_floor = self.current_floor
        self.current_floor = msg.data

        if prev_floor != self.current_floor:
            self.get_logger().info(f"🏢 엘리베이터 층 변경: {prev_floor}층 → {self.current_floor}층")
            if self.current_floor == self.target_floor and self.elevator_command_sent:
                self.elevator_moving = True
                self.get_logger().info(f"🎯 {self.target_floor}층 도착 완료 - 문 열림 대기 중...")

    def send_elevator_command(self):
        """엘리베이터 목표 층 이동 명령 전송"""
        self.door_was_open = False
        self.elevator_command_sent = True

        # gz topic 명령 실행 (목표 층 = 맨 왼쪽 숫자 - 1)
        elevator_command = str(self.target_floor)
        try:
            cmd = ['gz', 'topic', '-p', '/gazebo/world/elevator', '-m', f'data: "{elevator_command}"']
            subprocess.run(cmd, check=True)
            self.get_logger().info(f"✅ 엘리베이터 {self.target_floor}층 이동 명령 전송 완료")
        except subprocess.CalledProcessError as e:
            self.get_logger().error(f"❌ 엘리베이터 명령 전송 실패: {e}")
        except Exception as e:
            self.get_logger().error(f"❌ 예상치 못한 오류: {e}")

    def create_pose(self, x, y, yaw=0.0):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.orientation.z = math.sin(yaw/2)
        pose.pose.orientation.w = math.cos(yaw/2)
        return pose

    def get_current_position(self):
        """현재 위치를 반환"""
        try:
            # Nav2에서 현재 위치 가져오기
            current_pose = self.navigator.getCurrentPose()
            if current_pose:
                return (current_pose.pose.position.x, current_pose.pose.position.y)
        except:
            pass
        return None

def main(args=None):
    rclpy.init(args=args)
    node = TurtlebotMover()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
