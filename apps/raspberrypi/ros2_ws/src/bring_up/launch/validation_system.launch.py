import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess

# 모든 환경 설정 경로를 변수로 정의하여 관리
ROS_SETUP_SCRIPT = "/home/ssafy/git/S13P21C206/apps/raspberrypi/ros2_ws/install/setup.bash"
VENV_SITE_PACKAGES = "/home/ssafy/juno/.venv/lib/python3.12/site-packages"

def generate_launch_description():
    # 실행할 명령어를 생성하는 헬퍼 함수
    def create_sudo_command(pkg_name, node_name):
        # bash -c "명령1; 명령2; 명령3" 형태로 모든 것을 하나의 쉘 세션에서 실행
        # 핵심: PYTHONPATH를 직접 export하여 sudo 환경에 주입
        command_string = (
            f"source {ROS_SETUP_SCRIPT}; "
            f"export PYTHONPATH={VENV_SITE_PACKAGES}:$PYTHONPATH; "
            f"ros2 run {pkg_name} {node_name}"
        )
        return ['sudo', 'bash', '-c', command_string]

    return LaunchDescription([
        # nfc_pkg 노드 실행
        ExecuteProcess(
            cmd=create_sudo_command('nfc_pkg', 'nfc_reader_node'),
            output='screen'
        ),
        
        # yolo_pkg 노드 실행
        ExecuteProcess(
            cmd=create_sudo_command('yolo_pkg', 'yolo_validator_node'),
            output='screen'
        ),
        
        # servo_pkg 노드 실행
        ExecuteProcess(
            cmd=create_sudo_command('servo_pkg', 'servo_controller_node'),
            output='screen'
        ),
    ])