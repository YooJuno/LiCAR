import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, ExecuteProcess
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    turtlebot_launch_dir = os.path.join(get_package_share_directory('turtlebot3_gazebo'), 'launch')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_cartographer = get_package_share_directory('turtlebot3_cartographer')
    pkg_licar_bringup = get_package_share_directory('licar_bringup')

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    x_pose = LaunchConfiguration('x_pose', default='-2.0')
    y_pose = LaunchConfiguration('y_pose', default='-0.5')

    HOME_DIR = os.environ['HOME']
    world_hospital = HOME_DIR + '/aws-robomaker-hospital-world/worlds/hospital.world'
    world_hospital_second = HOME_DIR + '/aws-robomaker-hospital-world/worlds/hospital_two_floors.world'
    world_hospital_third = HOME_DIR + '/aws-robomaker-hospital-world/worlds/hospital_three_floors.world'
    print(world_hospital)

    gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': world_hospital_third}.items()
    )

    gzclient_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
        )
    )

    # 엘리베이터는 월드파일에 직접 포함됨 (spawn 불필요)

    # ROS2-Gazebo bridge for elevator control (GzString type)
    elevator_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/elevator@std_msgs/msg/String]/gazebo/world/elevator@gazebo.msgs.GzString'],
        name='elevator_bridge',
        output='screen'
    )

    # 엘리베이터 컨트롤러 노드 (ElevatorPlugin 충돌 방지로 완전 비활성화)
    # elevator_controller = Node(
    #     package='licar_bringup',
    #     executable='elevator_controller.py',
    #     name='elevator_controller',
    #     output='screen'
    # )

    # ros2_control 부분 제거 (SDF 내장 플러그인 사용)

    ld = LaunchDescription()

    # Add the commands to the launch description
    ld.add_action(gzserver_cmd)
    ld.add_action(gzclient_cmd)
    ld.add_action(elevator_bridge)
    # ld.add_action(elevator_controller)  # ElevatorPlugin 충돌 방지로 완전 비활성화

    return ld
