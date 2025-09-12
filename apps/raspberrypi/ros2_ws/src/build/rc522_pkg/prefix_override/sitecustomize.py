import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/ssafy/S13P21C206/apps/raspberrypi/ros2_ws/src/install/rc522_pkg'
