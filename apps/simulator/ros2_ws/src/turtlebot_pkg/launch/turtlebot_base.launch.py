#!/usr/bin/env python3
import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_dir = get_package_share_directory('turtlebot_pkg')

    mover_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_dir, 'src', 'turtlebot_pkg', 'turtlebot_mover.py'))
    )
    spawner_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_dir, 'src', 'turtlebot_pkg', 'turtlebot_spawner.py'))
    )

    ld = LaunchDescription()
    ld.add_action(mover_node)
    ld.add_action(spawner_node)
    return ld
