# LiCar Simulator

Gazebo 환경에서 AWS Hospital 맵을 불러와 Nav2를 수행하는 시나리오.

## Dev Env
- Ubunutu 22.04
- ROS2 Humble

## 1. ROS2 Installation
[Reference Link](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html#id4)
```bash
locale  # check for UTF-8

sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

locale  # verify settings
```
```bash
sudo apt install software-properties-common
sudo add-apt-repository universe
```
```bash
sudo apt update && sudo apt install curl -y
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo $VERSION_CODENAME)_all.deb" # If using Ubuntu derivates use $UBUNTU_CODENAME
sudo dpkg -i /tmp/ros2-apt-source.deb
```
```bash
sudo apt update
sudo apt upgrade

sudo apt install ros-humble-desktop
```


## 2. AWS Hospital Map installation
[Reference Link](https://github.com/aws-robotics/aws-robomaker-hospital-world/tree/ros2)
```bash
cd ~
git clone https://github.com/aws-robotics/aws-robomaker-hospital-world.git -b ros2
cd aws-robomaker-hospital-world
rosdep install --from-paths . --ignore-src -r -y
chmod +x setup.sh
./setup.sh
colcon build
```

## 3. TurtleSim Installation (HUMBLE)
[Reference Link](https://kimbrain.tistory.com/entry/%ED%84%B0%ED%8B%80%EB%B4%87-%EC%8A%A4%ED%84%B0%EB%94%94-1%EC%A3%BC%EC%B0%A8-%ED%84%B0%ED%8B%80%EB%B4%873-%EC%8B%9C%EB%AE%AC%EB%A0%88%EC%9D%B4%EC%85%98-%EB%93%80%ED%86%A0%EB%A6%AC%EC%96%BC-%EC%A7%84%ED%96%89%ED%95%98%EA%B8%B0)
```bash
cd ~
mkdir -p turtle_ws/src && cd turtle_ws/src

git clone https://github.com/ROBOTIS-GIT/turtlebot3.git -b humble
git clone https://github.com/ROBOTIS-GIT/turtlebot3_msgs.git -b humble
git clone https://github.com/ROBOTIS-GIT/turtlebot3_simulations.git -b humble

cd ..

sudo apt install python3-rosdep2
sudo apt install python3-colcon-common-extensions

rosdep init
rosdep update
rosdep install --from-paths src --ignore-src -r -y

colcon build --symlink-install && source install/local_setup.bash
```

## 4. Cartographer
```bash


```

## 5. Nav2 Installation
```bash
sudo apt install ros-humble-navigation2
sudo apt install ros-humble-nav2-bringup
sudo apt install ros-humble-turtlebot3-gazebo

# example
ros2 launch nav2_bringup tb3_simulation_launch.py headless:=False
```

## bashrc

```bash
# Linux
alias sb="source ~/.bashrc; echo \"bashrc is reloaded.\""

# ROS2 Paths
export ROS2_WS_PATH=$HOME/S13P21C206/apps/simulator/ros2_ws
export AWS_HOSPITAL_WS_PATH=$HOME/aws-robomaker-hospital-world
export TURTLE_WS_PATH=$HOME/turtle_ws

# ROS2 Init
alias humble="source /opt/ros/humble/setup.bash; echo \"ROS2 Humble is activated.\""
alias turtlebot="humble; source ${TURTLE_WS_PATH}/install/local_setup.bash; echo \"turtlebot workspace is activated.\""

# ROS2 Env
export TURTLEBOT3_MODEL=burger #
export GAZEBO_MODEL_PATH=${AWS_HOSPITAL_WS_PATH}/models:${AWS_HOSPITAL_WS_PATH}/fuel_models
# export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/opt/ros/humble/share/turtlebot3_gazebo/models # nav2 용
# export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:$HOME/turtle_ws/src/turtlebot3_simulations/turtlebot3_gazebo/models

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

export LIBGL_ALWAYS_SOFTWARE=1 
export QT_QPA_PLATFORM=xcb 
```