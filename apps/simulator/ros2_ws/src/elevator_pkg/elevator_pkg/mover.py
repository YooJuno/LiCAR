from geometry_msgs.msg import Pose, Point, Quaternion, Twist, Vector3
from gazebo_msgs.msg import ModelState
import rclpy
from rclpy.node import Node

class ElevatorMover(Node):
    def __init__(self):
        super().__init__('mover')
        self.pub = self.create_publisher(ModelState, '/gazebo/set_model_state', 10)
        self.timer = self.create_timer(0.1, self.move_up)
        self.z = 0.19

    def move_up(self):
        self.z += 0.01
        msg = ModelState()
        msg.model_name = 'car_1'
        msg.pose = Pose(position=Point(x=-1.49587, y=19.35, z=self.z),
                        orientation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0))
        msg.twist = Twist(linear=Vector3(), angular=Vector3())
        msg.reference_frame = 'world'
        self.pub.publish(msg)

def main():
    rclpy.init()
    node = ElevatorMover()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
