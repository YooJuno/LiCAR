import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess

# 모든 환경 설정 경로를 변수로 정의하여 관리
ROS_SETUP_SCRIPT = "/home/ssafy/git/S13P21C206/apps/raspberrypi/ros2_ws/install/setup.bash"
VENV_SITE_PACKAGES = "/home/ssafy/juno/.venv/lib/python3.12/site-packages"
ROS_DOMAIN_ID = "1"
RASPBERRY_PI_IP = "192.168.100.246" # <<--- 라즈베리 파이 IP로 수정하세요!
SIMULATOR_PC_IP = "192.168.100.145"   # <<--- 시뮬레이터 PC IP로 수정하세요!

def generate_launch_description():
    # 실행할 명령어를 생성하는 헬퍼 함수
    def create_sudo_command(pkg_name, executable_name, node_name):
        # bash -c "명령1; 명령2; ..." 형태로 모든 것을 하나의 쉘 세션에서 실행
        # PYTHONPATH 주입 + 노드 이름 재지정(Remapping)을 모두 포함
        command_string = (
            # 1. ROS 2 네트워크 환경 설정
            f"export ROS_DOMAIN_ID={ROS_DOMAIN_ID}; "
            f"export ROS_IP={RASPBERRY_PI_IP}; "
            f"export ROS_AUTOMATIC_DISCOVERY_RANGE=SUBSCRIBER; "
            f"export ROS_STATIC_PEERS={SIMULATOR_PC_IP}; "
            
            f"source {ROS_SETUP_SCRIPT}; "
            f"export PYTHONPATH={VENV_SITE_PACKAGES}:$PYTHONPATH; "
            f"ros2 run {pkg_name} {executable_name} --ros-args -r __node:={node_name}"
        )
        return ['sudo', 'bash', '-c', command_string]

    return LaunchDescription([
        # nfc_pkg 노드 실행
        ExecuteProcess(
            cmd=create_sudo_command(
                pkg_name='nfc_pkg', 
                executable_name='nfc_reader_node', 
                node_name='nfc_reader_node' # 이 노드의 이름을 'nfc_reader_node'로 강제
            ),
            output='screen'
        ),
        
        # yolo_pkg 노드 실행
        ExecuteProcess(
            cmd=create_sudo_command(
                pkg_name='yolo_pkg', 
                executable_name='yolo_validator_node', 
                node_name='yolo_validator_node' # 이 노드의 이름을 'yolo_validator_node'로 강제
            ),
            output='screen' 
        ),
        
        # servo_pkg 노드 실행
        ExecuteProcess(
            cmd=create_sudo_command(
                pkg_name='servo_pkg', 
                executable_name='servo_controller_node', 
                node_name='servo_controller_node' # 이 노드의 이름을 'servo_controller_node'로 강제
            ),
            output='screen'
        ),
    ])