# 터틀봇 엘리베이터 위에 올릴 수 있도록 위치 수정
```
    <model name="aws_robomaker_hospital_ramp_01_1">
      <include>
        <uri>model://aws_robomaker_hospital_ramp_01</uri>
        <static>true</static>
        <pose>-1.70996 16.1685 0 0 -0 0</pose>
      </include>
    </model>
```
```
# 포탈 삭제
# 엘리베이터 z축 0.01 낮추기(1층 기준 0.18)
```

# 참고
맵 실행
```
ros2 launch aws_robomaker_hospital_world licar.launch.py
```
move
```
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/cmd_vel
```
엘베 생성
```
ros2 run gazebo_ros spawn_entity.py \
  -entity car_1 \
  -file ~/aws-robomaker-hospital-world/models/licar_elevator/model.sdf \
  -x -1.49587 -y 19.35 -z 0.18
```
엘베 삭제
```
os2 service call /delete_entity gazebo_msgs/srv/DeleteEntity "{name: 'car_1'}"
```
자율주행
```
ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True map:=$HOME/S13P21C206/apps/simulator/maps/0915_1714/map.yaml
```