#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522


class RC522Node(Node):
    def __init__(self):
        super().__init__('rc522_node')
        self.publisher_ = self.create_publisher(String, 'rfid_data', 10)
        self.reader = SimpleMFRC522()
        self.get_logger().info('RC522 RFID node started')
        self.read_loop()

    def read_loop(self):
        while rclpy.ok():
            try:
                id, text = self.reader.read()
                msg = String()
                msg.data = f"ID: {id}, Text: {text.strip()}"
                self.publisher_.publish(msg)
                self.get_logger().info(f'Published: {msg.data}')
            except Exception as e:
                self.get_logger().error(f'Error: {e}')
            finally:
                GPIO.cleanup()


def main(args=None):
    rclpy.init(args=args)
    node = RC522Node()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
