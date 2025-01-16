import cv2
import paho.mqtt.client as mqtt
import numpy as np
import torch
import pickle

# Nastavenie MQTT klienta
MQTT_BROKER = "localhost"  # Adresa MQTT brokera
MQTT_PORT = 1883
MQTT_TOPIC = "obstacle_detection"

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    """Callback pre pripojenie k MQTT brokeru."""
    print(f"Pripojené k MQTT brokeru s kódom: {rc}")

def send_detection_data(detection_result):
    """Poslanie dát o detekcii cez MQTT."""
    client.publish(MQTT_TOPIC, pickle.dumps(detection_result))

# Pripojenie MQTT klienta
client.on_connect = on_connect
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()  # Spustenie MQTT klienta na pozadí

# Inicializácia modelu YOLOv8 pre detekciu
model = torch.hub.load('ultralytics/yolov8', 'yolov8n-seg')  # Použitie YOLOv8 modelu pre segmentáciu

# Funkcia na detekciu prekážok a rozdelenie obrazu na zóny
def detect_obstacles(frame):
    results = model(frame)  # Detekcia prekážok na obrázku
    # Získanie segmentovaných oblastí
    segments = results.pandas().xywh[0]
    
    # Zóny na analýzu: Ľavá, Stredná, Pravá
    height, width, _ = frame.shape
    left_zone = (0, 0, width // 3, height)  # Ľavá zóna
    center_zone = (width // 3, 0, 2 * width // 3, height)  # Stredná zóna
    right_zone = (2 * width // 3, 0, width, height)  # Pravá zóna

    # Inicializácia zón pre detekciu
    zone_status = {"left": False, "center": False, "right": False}

    # Skontroluj detekcie pre každý segment a urči, do ktorej zóny patrí
    for _, row in segments.iterrows():
        x_center = row['xcenter'] * width
        y_center = row['ycenter'] * height
        # Priradenie detekcie k zóne
        if left_zone[0] <= x_center <= left_zone[2]:
            zone_status["left"] = True
        if center_zone[0] <= x_center <= center_zone[2]:
            zone_status["center"] = True
        if right_zone[0] <= x_center <= right_zone[2]:
            zone_status["right"] = True

    return zone_status

# Hlavná slučka pre snímanie obrazu z kamery a detekciu prekážok
cap = cv2.VideoCapture(0)  # Používanie kamery (Raspberry Pi Camera alebo USB kamera)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    ret, frame = cap.read()  # Načítanie snímky
    if not ret:
        print("Nepodarilo sa načítať snímku")
        break

    # Detekcia prekážok v obraze
    zone_status = detect_obstacles(frame)
    
    # Zobrazenie výsledkov
    print(f"Detekcia prekážok v zónach: {zone_status}")

    # Poslanie výsledkov cez MQTT
    send_detection_data(zone_status)

    # Zobrazenie výsledného obrazu s detekciami (nepovinné)
    cv2.imshow('Detekcia prekážok', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
