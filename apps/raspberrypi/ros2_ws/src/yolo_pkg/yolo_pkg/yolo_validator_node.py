#!/home/ssafy/juno/.venv/bin/python

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from ultralytics import YOLO
import cv2
import json
import torch
import os

class YoloValidatorNode(Node):
    def __init__(self):
        super().__init__('yolo_validator_node')
        
        self.drug_list_subscription = self.create_subscription(String, 'drug_list_request', self.drug_list_callback, 10)
        self.status_publisher = self.create_publisher(Bool, 'validation_status', 10)
        
        try:
            self.device = 'cpu'
            self.get_logger().info(f"Using device: {self.device}")
            model_path = '/home/ssafy/Desktop/new/best.pt'
            self.model = YOLO(model_path)
            self.model.to(self.device)
            self.class_names = self.model.names
            self.get_logger().info("================ MODEL INFO ================")
            self.get_logger().info(f"Model loaded successfully from {model_path}")
            self.get_logger().info(f"Model Class Names: {self.class_names}")
            self.get_logger().info("============================================")
        except Exception as e:
            self.get_logger().error(f"FATAL: Failed to load YOLO model: {e}")
            return

        self.cap = None
        self.gui_enabled = False
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.get_logger().error("Cannot open camera. Node will run without validation capability.")
                self.cap = None
            else:
                # --- 수정된 부분 1: 카메라 캡처 해상도 설정 ---
                # 라즈베리 파이에서 지원하는 낮은 해상도 중 하나인 320x240으로 설정 시도
                # 원하는 해상도로 변경 가능 (예: 640, 480)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
                width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                self.get_logger().info(f"Camera resolution set to: {width}x{height}")
                
                if 'DISPLAY' in os.environ:
                    self.window_name = "YOLOv8 Detection Screen"
                    cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
                    self.gui_enabled = True
                    self.get_logger().info("Display environment detected. GUI is enabled.")
                else:
                    self.get_logger().info("No display environment. GUI is disabled.")

        except Exception as e:
            self.get_logger().error(f"Failed to initialize camera or GUI: {e}")
            self.gui_enabled = False
            if self.cap: self.cap.release()
            self.cap = None

        self.target_pills = {}
        self.is_validating = False
        
        self.timer = self.create_timer(0.1, self.process_frame)
        self.get_logger().info('YOLO Validator Node has been started.')

        initial_status_msg = Bool()
        initial_status_msg.data = True
        self.status_publisher.publish(initial_status_msg)
        self.get_logger().info("Published initial status=True. System is ready.")

    def drug_list_callback(self, msg):
        # ... (이전과 동일)
        if self.cap is None:
            self.get_logger().error("Camera is not available. Cannot start validation.")
            status_msg = Bool(); status_msg.data = True
            self.status_publisher.publish(status_msg)
            return
        
        try:
            drug_names = json.loads(msg.data)
            if not isinstance(drug_names, list) or not drug_names: return
            self.get_logger().info("=============================================")
            self.get_logger().info(f" Received New Drug List Request: {drug_names} ")
            self.get_logger().info("=============================================")
            self.target_pills = {name: False for name in drug_names}
            self.is_validating = True
            status_msg = Bool(); status_msg.data = False
            self.status_publisher.publish(status_msg)
            self.get_logger().info("Published validation_status=False to open the door.")
            self.get_logger().info(f"New validation session started. Target drugs: {list(self.target_pills.keys())}")
        except Exception as e:
            self.get_logger().error(f"Error in drug_list_callback: {e}")

    def process_frame(self):
        if not self.is_validating or not self.cap:
            return
            
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().warn("Failed to grab frame from camera")
            return
        
        results_generator = self.model(frame, stream=True, verbose=False, conf=0.25, device=self.device, imgsz=192)
        
        annotated_frame = frame.copy()
        for results in results_generator:
            if self.gui_enabled:
                annotated_frame = results.plot()
            
            for box in results.boxes:
                class_id = int(box.cls[0])
                pill_name = self.class_names.get(class_id, "Unknown")
                
                if pill_name in self.target_pills and not self.target_pills[pill_name]:
                    self.target_pills[pill_name] = True
                    self.get_logger().info(f"Found Target: {pill_name}! Status: {self.target_pills}")

        # --- 수정된 부분: 이 if문의 들여쓰기를 바깥으로 뺌 ---
        if self.target_pills and all(self.target_pills.values()):
            self.get_logger().info('SUCCESS: All target drugs have been detected!')
            status_msg = Bool(); status_msg.data = True
            self.status_publisher.publish(status_msg)
            
            self.is_validating = False
            self.target_pills = {}
            
            if self.gui_enabled:
                writable_frame = annotated_frame.copy()
                cv2.putText(writable_frame, "VALIDATION SUCCESS!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                annotated_frame = writable_frame

        if self.gui_enabled:
            cv2.imshow(self.window_name, annotated_frame)
            cv2.waitKey(1)
            
    def destroy_node(self):
        # ... (이전과 동일)
        if self.cap: self.cap.release()
        if self.gui_enabled: cv2.destroyAllWindows()
        super().destroy_node()

def main(args=None):
    # ... (이전과 동일)
    rclpy.init(args=args)
    yolo_validator_node = YoloValidatorNode()
    try: rclpy.spin(yolo_validator_node)
    except KeyboardInterrupt: pass
    finally:
        yolo_validator_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()