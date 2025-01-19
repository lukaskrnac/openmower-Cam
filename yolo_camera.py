import numpy as np
import cv2
from ultralytics import YOLO
import paho.mqtt.client as mqtt
import pickle
import time
from picamera2 import Picamera2

# 1. Načítanie YOLOv8 modelu
model = YOLO("best_ncnn_model",task='segment')  # Nahraď cestou k svojmu modelu

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


# Initialize the Picamera2
picam2 = Picamera2()
picam2.preview_configuration.main.size = (1280, 960)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

# Pripojenie MQTT klienta
client.on_connect = on_connect
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()  # Spustenie MQTT klienta na pozadí

# 2. Funkcia na generovanie lichobežníkových zón
def create_zones(image_shape):
    h, w = image_shape[:2]
    zones = []

    zones.append(np.array([[0, h], [int(w * 0.25), int(h * 0.5)], [int(w * 0.75), int(h * 0.5)], [w, h]], np.int32))  # Spodná zóna
    zones.append(np.array([[int(w * 0.25), int(h * 0.5)], [int(w * 0.35), int(h * 0.3)], [int(w * 0.65), int(h * 0.3)], [int(w * 0.75), int(h * 0.5)]], np.int32))  # Druhá zóna
    zones.append(np.array([[int(w * 0.35), int(h * 0.3)], [int(w * 0.4), int(h * 0.15)], [int(w * 0.6), int(h * 0.15)], [int(w * 0.65), int(h * 0.3)]], np.int32))  # Tretia zóna
    zones.append(np.array([[int(w * 0.4), int(h * 0.15)], [int(w * 0.5), 0], [int(w * 0.5), 0], [int(w * 0.6), int(h * 0.15)]], np.int32))  # Horná zóna

    return zones

# 3. Funkcia na výpočet obsadenia zóny
def calculate_occupancy(mask, zones):
    zone_areas = []
    for zone in zones:
        zone_mask = np.zeros(mask.shape[:2], dtype=np.uint8)
        cv2.fillPoly(zone_mask, [zone], 1)
        overlapping_pixels = np.sum(mask * zone_mask)
        zone_pixels = np.sum(zone_mask)
        occupancy = overlapping_pixels / zone_pixels if zone_pixels > 0 else 0
        zone_areas.append(occupancy * 100)  # Percentá
    return zone_areas

# 4. Načítanie obrazu

iObr = 0
# 5. Hlavná slučka
while True:
    start_time = time.time()
    image = picam2.capture_array()
    image = cv2.resize(image, (320,240)) 

    height, width, channels = image.shape

    print(f"Šírka: {width}, Výška: {height}, Kanály: {channels}")
    # 6. Detekcia YOLOv8
    results = model(image,imgsz=320)

    # Získanie masiek ako NumPy pole
    masks = []
    if results[0].masks:
        masks = results[0].masks.data.cpu().numpy()
    else:
        print("Žiadne masky neboli detegované!")

    # 7. Lichobežníkové zóny
    zones = create_zones(image.shape)

    # Zmena rozmerov masiek na veľkosť pôvodného obrazu
    resized_masks = []
    for mask in masks:
        resized_mask = mask[40:280, 0:320]
        #resized_mask = cv2.resize(mask, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)
        resized_masks.append(resized_mask)
    # 8. Výpočet obsadenia pre zóny
    vysledky = []
    for i, resized_mask in enumerate(resized_masks):
        zone_occupancies = calculate_occupancy(resized_mask, zones)
        vysledky.append(zone_occupancies)

    send_detection_data(vysledky)

    # 9. Vizualizácia
    output_image = image.copy()

    # Vyznačenie masiek
    if results[0].masks:
        for mask in results[0].masks:
            mask = mask.data.cpu().numpy()[0]
            colored_mask = np.zeros_like(image, dtype=np.uint8)
            colored_mask[resized_mask > 0.5] = [0, 255, 0]  # Zelená farba pre masky
            output_image = cv2.addWeighted(output_image, 1, colored_mask, 0.5, 0)

    # Vykreslenie zón
    for i, zone in enumerate(zones):
        cv2.polylines(output_image, [zone], isClosed=True, color=(255, 0, 0), thickness=2)
    
    iObr+=1
    filename = f"garden_processed_{iObr}.jpg"
    #success = cv2.imwrite(filename, output_image)

    # Over, či bol obrázok úspešne uložený
    if success:
        print(f"Obrázok {filename} bol úspešne uložený.")
    else:
        print(f"Chyba pri ukladaní obrázka {filename}.")

    cycle_time = time.time() - start_time
    print(f"Čas cyklu: {cycle_time:.2f} sekundy")

    if iObr>20 :
        break

# Uvoľnenie zdrojov
client.loop_stop()
