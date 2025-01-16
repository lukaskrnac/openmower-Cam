import cv2
import numpy as np
import picamera
import picamera.array
import zmq
from ultralytics import YOLO

# Inicializácia YOLOv8n modelu
model = YOLO('yolov8n-seg.pt')  # Uisti sa, že máš správnu cestu k modelu

# ZeroMQ setup
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5555")  # Adresa a port pre ROS uzol

# Nastavenie kamery
camera = picamera.PICamera()
camera.resolution = (640, 480)  # Nastav rozlíšenie podľa potreby
camera.framerate = 30

def process_frame(frame):
    # Detekcia objektov cez YOLOv8
    results = model(frame)
    
    # Získanie segmentovaných masiek a predikcií
    masks = results.masks
    detections = results.xywh[0]  # Výstupy detekcie

    # Rozdelenie obrazu na 3 zóny
    h, w, _ = frame.shape
    left_zone = frame[:, :w//3]
    center_zone = frame[:, w//3:2*w//3]
    right_zone = frame[:, 2*w//3:]
    
    # Vyhodnotenie, či je prekážka v každej zóne
    zones_status = {"left": False, "center": False, "right": False}

    for mask in masks:
        mask = mask.numpy().astype(np.uint8) * 255  # Prevod masky na binárnu hodnotu

        # Zistenie, v ktorých zónach je maska
        left_mask = mask[:, :w//3]
        center_mask = mask[:, w//3:2*w//3]
        right_mask = mask[:, 2*w//3:]

        if np.any(left_mask):  # Ak existuje aspoň jedna časť masky v ľavej zóne
            zones_status["left"] = True
        if np.any(center_mask):  # Ak existuje aspoň jedna časť masky v strednej zóne
            zones_status["center"] = True
        if np.any(right_mask):  # Ak existuje aspoň jedna časť masky v pravej zóne
            zones_status["right"] = True

    return zones_status

def main():
    try:
        while True:
            with picamera.array.PiRGBArray(camera) as stream:
                # Snímka z kamery
                camera.capture(stream, format='bgr')
                frame = stream.array

                # Spracovanie snímky
                zones_status = process_frame(frame)

                # Odoslanie výsledku cez ZeroMQ
                socket.send_string(str(zones_status))

    except KeyboardInterrupt:
        print("Zastavenie detekcie.")
        camera.close()

if __name__ == "__main__":
    main()
