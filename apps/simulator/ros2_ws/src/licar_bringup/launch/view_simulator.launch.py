import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, ExecuteProcess, SetEnvironmentVariable
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

SIMULATOR_BRINGUP_PKG = 'licar_bringup' 
CYCLONEDDS_URI = os.path.join(
    get_package_share_directory(SIMULATOR_BRINGUP_PKG).replace(f'/src/licar_bringup', ''),
    'cyclonedds.xml'
)


# Load environment variables from .env file
HOME_PATH = os.environ['HOME']
env_file = os.path.join(HOME_PATH, 'S13P21C206', '.env')

# Simple .env file parser
def load_env(file_path):
    env_vars = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    env_vars[key] = value
    return env_vars

env_vars = load_env(env_file)
ROS_DOMAIN_ID = env_vars.get("ROS_DOMAIN_ID")
SIMULATOR_PC_IP = env_vars.get("SIMULATOR_PC_IP")
RASPBERRY_PI_IP = env_vars.get("RASPBERRY_PI_IP")

def generate_launch_description():
    turtlebot_launch_dir = os.path.join(get_package_share_directory('turtlebot3_gazebo'), 'launch')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_cartographer = get_package_share_directory('turtlebot3_cartographer')
    pkg_licar_bringup = get_package_share_directory('licar_bringup')

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    x_pose = LaunchConfiguration('x_pose', default='-2.0')
    y_pose = LaunchConfiguration('y_pose', default='-0.5')

    world_hospital = HOME_PATH + '/S13P21C206/apps/simulator/aws-robomaker-hospital-world/worlds/hospital.world'
    world_hospital_third = HOME_PATH + '/S13P21C206/apps/simulator/aws-robomaker-hospital-world/worlds/hospital_three_floors.world'

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
        arguments=['/elevator@std_msgs/msg/String@gazebo.msgs.GzString'],
        name='elevator_bridge',
        output='screen'
    )

    ld = LaunchDescription()
    ld.add_action(SetEnvironmentVariable('ROS_DOMAIN_ID', ROS_DOMAIN_ID))
    ld.add_action(SetEnvironmentVariable('ROS_IP', SIMULATOR_PC_IP))
    ld.add_action(SetEnvironmentVariable('ROS_AUTOMATIC_DISCOVERY_RANGE', 'SUBSCRIBER'))
    ld.add_action(SetEnvironmentVariable('ROS_STATIC_PEERS', RASPBERRY_PI_IP))

    ld.add_action(SetEnvironmentVariable('RMW_IMPLEMENTATION', 'rmw_cyclonedds_cpp'))
    ld.add_action(SetEnvironmentVariable('CYCLONEDDS_URI', CYCLONEDDS_URI))
    # Add the commands to the launch description
    ld.add_action(gzserver_cmd)
    ld.add_action(gzclient_cmd)
    ld.add_action(elevator_bridge)

    return ld
