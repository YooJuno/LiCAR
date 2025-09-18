#!/home/ssafy/juno/.venv/bin/python

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from ultralytics import YOLO
import cv2
import json
import torch # torch를 import하여 device를 명시적으로 설정

class YoloValidatorNode(Node):
    def __init__(self):
        super().__init__('yolo_validator_node')
        
        # ... (Subscription, Publisher는 이전과 동일)
        self.drug_list_subscription = self.create_subscription(String, 'drug_list_request', self.drug_list_callback, 10)
        self.status_publisher = self.create_publisher(Bool, 'validation_status', 10)
        
        # --- 수정된 부분: 모델 로드 및 device 설정 ---
        try:
            # 1. Device를 명시적으로 CPU로 설정 (라즈베리 파이 환경)
            self.device = 'cpu'
            self.get_logger().info(f"Using device: {self.device}")
            
            # 2. 모델 파일의 절대 경로를 정확하게 지정
            model_path = '/home/ssafy/Desktop/best.pt'
            self.model = YOLO(model_path)
            
            # 3. 모델을 지정된 device로 이동
            self.model.to(self.device)
            
            self.class_names = self.model.names
            self.get_logger().info("================ MODEL INFO ================")
            self.get_logger().info(f"Model loaded successfully from {model_path}")
            self.get_logger().info(f"Model Class Names: {self.class_names}")
            self.get_logger().info("============================================")
            
        except Exception as e:
            self.get_logger().error(f"Failed to load YOLO model: {e}")
            return

        # ... (카메라, GUI 창 설정은 이전과 동일)
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened(): self.get_logger().error("Cannot open camera")
        self.window_name = "YOLOv8 Detection Screen"
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        
        self.target_pills = {}
        self.is_validating = False
        
        self.timer = self.create_timer(0.1, self.process_frame)
        self.get_logger().info('YOLO Validator Node has been started.')

    def drug_list_callback(self, msg):
        # ... (이전과 동일)
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
            self.get_logger().info(f"New validation session started. Target drugs: {list(self.target_pills.keys())}")
        except Exception as e:
            self.get_logger().error(f"Error in drug_list_callback: {e}")

    def process_frame(self):
        if not self.cap or not self.cap.isOpened(): return

        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().warn("Failed to grab frame from camera")
            return
        
        annotated_frame = frame.copy()
        
        if self.is_validating:
            # --- 수정된 부분: stream=True 추가 및 device 명시 ---
            results_generator = self.model(frame, stream=True, verbose=False, conf=0.1, device=self.device)
            
            # stream=True는 결과를 generator로 반환하므로, for 루프로 처리
            for results in results_generator:
                annotated_frame = results.plot()
                
                for box in results.boxes:
                    class_id = int(box.cls[0])
                    pill_name = self.class_names[class_id]
                    
                    if pill_name in self.target_pills and not self.target_pills[pill_name]:
                        self.target_pills[pill_name] = True
                        self.get_logger().info(f"Found Target: {pill_name}! Status: {self.target_pills}")

            if self.target_pills and all(self.target_pills.values()):
                self.get_logger().info('SUCCESS: All target drugs have been detected!')
                status_msg = Bool(); status_msg.data = True
                self.status_publisher.publish(status_msg)
                self.is_validating = False
                self.target_pills = {}
                cv2.putText(annotated_frame, "VALIDATION SUCCESS!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

        cv2.imshow(self.window_name, annotated_frame)
        cv2.waitKey(1)

    def destroy_node(self):
        # ... (이전과 동일)
        self.cap.release()
        cv2.destroyAllWindows()
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