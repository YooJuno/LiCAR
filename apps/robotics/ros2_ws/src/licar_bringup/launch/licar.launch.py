from launch import LaunchDescription
from launch.actions import ExecuteProcess, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
import os

def generate_launch_description():
    gui_arg    = DeclareLaunchArgument('gui',     default_value='true')
    paused_arg = DeclareLaunchArgument('paused',  default_value='false')
    verb_arg   = DeclareLaunchArgument('verbose', default_value='false')
    world_arg  = DeclareLaunchArgument(
        'world',
        default_value=os.path.join(
            '/home/juno/sim_ws/src/aws-robomaker-hospital-world/worlds',
            'hospital.world'
        )
    )

    gzserver = ExecuteProcess(
        cmd=[
            'gzserver',
            LaunchConfiguration('world'),
            ['--verbose' if LaunchConfiguration('verbose') == 'true' else ''],
            ['-u' if LaunchConfiguration('paused') == 'true' else ''],
            '-s', 'libgazebo_ros_factory.so'
        ],
        output='screen'
    )

    gzclient = ExecuteProcess(
        cmd=['gzclient'],
        output='screen'
    )

    rviz = ExecuteProcess(
        cmd=['rviz2'],
        output='screen'
    )

    return LaunchDescription([
        gui_arg, 
        paused_arg, 
        verb_arg, 
        world_arg,
        gzserver, 
        gzclient,
        rviz
    ])
