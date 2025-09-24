import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    # 패키지 경로
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_turtlebot3_gazebo = get_package_share_directory('turtlebot3_gazebo')
    pkg_elevator = get_package_share_directory('elevator_pkg')
    pkg_turtlebot = get_package_share_directory('turtlebot_pkg')

    # Gazebo world 파일 체크
    HOME_PATH = os.environ['HOME']
    world_hospital_third = HOME_PATH + '/S13P21C206/apps/simulator/aws-robomaker-hospital-world/worlds/hospital_three_floors.world'
    
    # World 파일이 없으면 기본 world 사용
    launch_arguments = {}
    if os.path.exists(world_hospital_third):
        launch_arguments['world'] = world_hospital_third
        launch_arguments['verbose'] = 'true'
    else:
        print(f"⚠️  World 파일을 찾을 수 없습니다: {world_hospital_third}")
        print("기본 empty world를 사용합니다.")
        launch_arguments['verbose'] = 'true'

    # Gazebo 실행
    gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')),
        launch_arguments=launch_arguments.items()
    )

    gzclient_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py'))
    )

    # 터틀봇 스폰 (지연 실행)
    turtlebot_spawn = TimerAction(
        period=3.0,  # 3초 후 실행
        actions=[
            Node(
                package='gazebo_ros',
                executable='spawn_entity.py',
                arguments=[
                    '-entity', 'turtlebot3_burger',
                    '-file', os.path.join(pkg_turtlebot3_gazebo, 'models', 'turtlebot3_burger', 'model.sdf'),
                    '-x', '-5.0',  # 원점으로 변경
                    '-y', '-2.0',
                    '-z', '0.01',
                    '-unpause'  # 자동 시작
                ],
                output='screen'
            )
        ]
    )

    # Elevator 노드
    elevator_node = Node(
        package='elevator_pkg',
        executable='door_state_converter_node',
        name='door_state_converter',
        output='screen'
    )

    # Turtlebot 노드들 (스폰 후 실행)
    turtlebot_main = TimerAction(
        period=5.0,  # 5초 후 실행
        actions=[
            Node(
                package='turtlebot_pkg',
                executable='main',
                name='turtlebot_main',  # name 변경
                output='screen'
            )
        ]
    )

    turtlebot_mover = TimerAction(
        period=5.0,  # 5초 후 실행
        actions=[
            Node(
                package='turtlebot_pkg',
                executable='turtlebot_mover',
                name='turtlebot_mover_node',  # name 변경으로 충돌 방지
                output='screen'
            )
        ]
    )

    # LaunchDescription에 추가
    ld = LaunchDescription()
    ld.add_action(gzserver_cmd)
    ld.add_action(gzclient_cmd)
    ld.add_action(turtlebot_spawn)
    ld.add_action(elevator_node)
    ld.add_action(turtlebot_main)
    ld.add_action(turtlebot_mover)

    return ld