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

    MAP_DIR = os.environ['HOME']
    world_hospital = '~/S13P21C206/apps/simulator/aws-robomaker-hospital-world/worlds/hospital.world'
    world_hospital_third = '~/S13P21C206/apps/simulator/aws-robomaker-hospital-world/worlds/hospital_three_floors.world'

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

    # ROS2-Gazebo bridge for elevator control (GzString type)
    elevator_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/elevator@std_msgs/msg/String]/gazebo/world/elevator@gazebo.msgs.GzString'],
        name='elevator_bridge',
        output='screen'
    )

    ld = LaunchDescription()

    # Add the commands to the launch description
    ld.add_action(gzserver_cmd)
    ld.add_action(gzclient_cmd)
    ld.add_action(elevator_bridge)

    return ld
