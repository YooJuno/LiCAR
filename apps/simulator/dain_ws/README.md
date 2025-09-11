# command
- start
```
ros2 launch aws_robomaker_hospital_world turtlebot3_hospital.launch.py \
  use_sim_time:=true gui:=true tb3_model:=burger x_pose:=-5.0 y_pose:=-5.0 z_pose:=0.6
```
- move
```
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/cmd_vel
```
# ~/.bashrc
```
# Linux
alias sb="source ~/.bashrc; echo \"bashrc is reloaded.\""

# ROS2 Paths
export ROS2_WS_PATH=/home/dain/ros2_ws
export AWS_HOSPITAL_PATH=/home/dain/ros2_ws/src/aws-robomaker-hospital-world
export TURTLE_WS_PATH=/home/dain/turtle_ws

# ROS2 Init
alias humble="source /opt/ros/humble/setup.bash; ros_domain; echo \"ROS2 Humble is activated.\""
alias turtlebot="humble; source ${TURTLE_WS_PATH}/install/local_setup.bash; echo \"turtlebot workspace is activated.\""

# ROS2 Env
export TURTLEBOT3_MODEL=burger
export GAZEBO_MODEL_PATH=${AWS_HOSPITAL_PATH}/models:${AWS_HOSPITAL_PATH}/fuel_models
export ROS_DOMAIN_ID=1

# ROS2 Source
source /opt/ros/humble/setup.bash
source ${AWS_HOSPITAL_PATH}/install/local_setup.bash
source ${ROS2_WS_PATH}/install/local_setup.bash
source ${TURTLE_WS_PATH}/install/local_setup.bash
source /usr/share/gazebo/setup.sh

# ROS2 Tools
alias cb='cd ${ROS2_WS_PATH} && colcon build --symlink-install && source install/local_setup.bash && echo "ros2 build success"'
alias killgazebo="killall gzserver gzclient"

```

# map
- scan
```
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true
```
- RViz2
```
rviz2 --ros-args -p use_sim_time:=true
```
RViz2 설정:
Fixed Frame: map
Displays 추가
Map → topic: /map
LaserScan → topic: /scan (Queue Size 100↑ 권장, QoS는 기본(RELIABLE)로 시작)
TF / RobotModel(선택)
상단 Time 패널에서 Sim Time이 체크돼 있는지 확인.

- twist move
```
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -r cmd_vel:=/cmd_vel -p speed:=0.2 -p turn:=1.0
  ```


- map save
```
mkdir -p ~/maps
ros2 run nav2_map_server map_saver_cli -f ~/maps/hospital_map
```

---
### history
- 모든 기존 Gazebo 꺼두기
pkill -f gzserver; pkill -f gzclient

- 실행
```
pkill -9 gzserver gzclient 2>/dev/null || true
[ -f ~/ros2_ws/install/setup.bash ] && source ~/ros2_ws/install/setup.bash
gzserver "$(ros2 pkg prefix aws_robomaker_hospital_world)/share/aws_robomaker_hospital_world/worlds/hospital.world" \
  -s libgazebo_ros_api_plugin.so \
  -s libgazebo_ros_factory.so

```
```
gzclient
```
```
source /opt/ros/humble/setup.bash
source ~/turtle_ws/install/setup.bash
export TURTLEBOT3_MODEL=burger

ros2 run robot_state_publisher robot_state_publisher \
  $(ros2 pkg prefix turtlebot3_description)/share/turtlebot3_description/urdf/turtlebot3_${TURTLEBOT3_MODEL}.urdf \
  --ros-args -p use_sim_time:=true
```
```
ros2 run gazebo_ros spawn_entity.py \
  -entity tb3_h \
  -file $(ros2 pkg prefix turtlebot3_gazebo)/share/turtlebot3_gazebo/models/turtlebot3_${TURTLEBOT3_MODEL}/model.sdf \
  -x -5.0 -y -7.0 -z 0.6 -Y 1.57
```
- scan
```
ros2 topic list | grep scan
ros2 topic echo /scan --once
```
- move
```
ros2 topic pub /cmd_vel geometry_msgs/Twist \
'{linear: {x: 0.2}, angular: {z: 0.3}}' -r 10
```
- stop
```
ros2 topic pub /cmd_vel geometry_msgs/Twist '{ }' -1
```

---
