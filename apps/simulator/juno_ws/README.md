# Robotics Project Workspace

이 프로젝트는 ROS 2 기반의 로봇 소프트웨어 개발을 위한 여러 워크스페이스로 구성되어 있습니다.

## 워크스페이스 구조

- **ros2_ws**  
    ROS 2 패키지 개발 및 빌드를 위한 메인 워크스페이스입니다.  
    주요 ROS 2 노드, 메시지, 서비스 등이 이곳에 위치합니다.


## 참고

- ROS 2 공식 문서: https://docs.ros.org/en/foxy/index.html
- Gazebo 공식 문서: https://gazebosim.org/docs

각 워크스페이스별 상세 내용은 해당 디렉터리의 README.md를 참고하세요.

## TurtleSim Installation (HUMBLE)
```bash
$ cd ~
$ mkdir -p turtle_ws/src && cd turtle_ws/src

$ git clone https://github.com/ROBOTIS-GIT/turtlebot3.git -b humble
$ git clone https://github.com/ROBOTIS-GIT/turtlebot3_msgs.git -b humble
$ git clone https://github.com/ROBOTIS-GIT/turtlebot3_simulations.git -b humble

$ cd ..

$ rosdep init
$ rosdep update
$ rosdep install --from-paths src --ignore-src -r -y

$ colcon build --symlink-install && source install/local_setup.bash
```

## Nav2 Installation
```bashrc

```

## bashrc

```bash

# Linux
alias sb="source ~/.bashrc; echo \"bashrc is reloaded.\""


# ROS2 Paths
export ROS2_WS_PATH=/home/juno/S13P21C206/apps/simulator/juno_ws
export AWS_HOSPITAL_WS_PATH=/home/juno/aws-robomaker-hospital-world
export TURTLE_WS_PATH=/home/juno/turtle_ws

# ROS2 Init
alias humble="source /opt/ros/humble/setup.bash; echo \"ROS2 Humble is activated.\""
alias turtlebot="humble; source ${TURTLE_WS_PATH}/install/local_setup.bash; echo \"turtlebot workspace is activated.\""

# ROS2 Env
export TURTLEBOT3_MODEL=burger #
export GAZEBO_MODEL_PATH=${AWS_HOSPITAL_WS_PATH}/models:${AWS_HOSPITAL_WS_PATH}/fuel_models
# export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/opt/ros/humble/share/turtlebot3_gazebo/models # nav2 용
# export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/home/juno/turtle_ws/src/turtlebot3_simulations/turtlebot3_gazebo/models

export ROS_DOMAIN_ID=1

# ROS2 Source
source /opt/ros/humble/setup.bash
source ${AWS_HOSPITAL_WS_PATH}/install/local_setup.bash
source ${ROS2_WS_PATH}/install/local_setup.bash
source ${TURTLE_WS_PATH}/install/local_setup.bash
source /usr/share/gazebo/setup.sh

# ROS2 Tools
alias cb='cd ${ROS2_WS_PATH} && colcon build --symlink-install && source install/local_setup.bash && echo "ros2 build success"'
alias killgazebo="killall gzserver gzclient"

```