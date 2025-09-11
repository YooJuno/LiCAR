# Robotics Project Workspace

이 프로젝트는 ROS 2 기반의 로봇 소프트웨어 개발을 위한 여러 워크스페이스로 구성되어 있습니다.

## 워크스페이스 구조

- **ros2_ws**  
    ROS 2 패키지 개발 및 빌드를 위한 메인 워크스페이스입니다.  
    주요 ROS 2 노드, 메시지, 서비스 등이 이곳에 위치합니다.

- **sim_ws**  
    시뮬레이션 환경 구축을 위한 워크스페이스입니다.  
    Gazebo, RViz 등 시뮬레이터 관련 패키지와 설정 파일이 포함됩니다.

- **turtle_ws**  
    튜토리얼 및 테스트용 패키지들이 포함된 워크스페이스입니다.  
    예제 코드와 실습용 패키지들이 위치합니다.

## 시작하기

1. 각 워크스페이스 디렉터리로 이동합니다.
2. `colcon build` 명령어로 빌드합니다.
3. 환경설정 파일을 소스합니다.
     ```bash
     source install/setup.bash
     ```

## 참고

- ROS 2 공식 문서: https://docs.ros.org/en/foxy/index.html
- Gazebo 공식 문서: https://gazebosim.org/docs

각 워크스페이스별 상세 내용은 해당 디렉터리의 README.md를 참고하세요.


## bashrc

```bash
# Linux
alias sb="source ~/.bashrc; echo \"bashrc is reloaded.\""

# ROS2 Init
alias humble="source /opt/ros/humble/setup.bash; ros_domain; echo \"ROS2 Humble is activated.\""

# ROS2 Paths
export ROS2_WS_PATH=/home/juno/S13P21C206/apps/robotics/ros2_ws
export AWS_HOSPITAL_PATH=/home/juno/aws-robomaker-hospital-world

# ROS2 Env
export TURTLEBOT3_MODEL=burger #
export GAZEBO_MODEL_PATH=${AWS_HOSPITAL_PATH}/models:${AWS_HOSPITAL_PATH}/fuel_models
export ROS_DOMAIN_ID=1

# ROS2 Source
source /opt/ros/humble/setup.bash
source ${ROS2_WS_PATH}/install/local_setup.bash

# ROS2 Tools
alias cb='cd ${ROS2_WS_PATH} && colcon build --symlink-install && source install/local_setup.bash && echo "ros2 build success"'
alias killgazebo="killall gzserver gzclient"
```