import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
from ultralytics import YOLO
import cv2

class CameraProcessingNode:
    def __init__(self):
        # Inicializácia ROS uzla
        rospy.init_node('camera_processing_node')

        # Publikovanie príkazu
        self.command_pub = rospy.Publisher('/robot/command', String, queue_size=10)

        # CvBridge na konverziu ROS obrazov na OpenCV formát
        self.bridge = CvBridge()

        # Načítanie YOLOv8 modelu
        self.model = YOLO('yolov8n.pt')  # Použite YOLOv8 nano model

        # Inicializácia webkamery
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            rospy.logerr("Nepodarilo sa otvoriť webkameru.")
            rospy.signal_shutdown("Webkamera nefunguje.")

        rospy.loginfo("Uzol je pripravený a čaká na dáta z kamery.")

    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            rospy.logerr("Nepodarilo sa načítať obraz z kamery.")
            return

        # Spracovanie obrazu YOLOv8
        results = self.model(frame)

        # Analýza výsledkov detekcie
        detections = results[0].boxes  # Získanie detegovaných objektov

        stop_detected = False
        for box in detections:
            cls = box.cls.cpu().numpy()  # Trieda objektu
            confidence = box.conf.cpu().numpy()  # Istota detekcie

            # Príklad: Ak trieda 0 (napr. osoba) je detegovaná, vydaj STOP
            if int(cls) == 0 and confidence > 0.5:
                stop_detected = True
                break

        # Publikovanie príkazu
        command = "stop" if stop_detected else "go"
        self.command_pub.publish(command)
        rospy.loginfo(f"Publikovaný príkaz: {command}")

    def run(self):
        rate = rospy.Rate(10)  # Frekvencia spracovania (10 Hz)
        while not rospy.is_shutdown():
            self.process_frame()
            rate.sleep()

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        node = CameraProcessingNode()
        node.run()
    except rospy.ROSInterruptException:
        pass
