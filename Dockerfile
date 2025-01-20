# Použitie ROS Noetic obrazu (založené na Ubuntu 20.04)
FROM fsodano79/raspbian:bullseye-20230101

# Nastavenie pracovného adresára
WORKDIR /app

# Aktualizácia systému balíkov a systémových závislostí
RUN apt-get update && apt-get install \
    python3 \
    python3-pip \
    python3-picamera2

# Inštalácia Python knižníc cez pip
RUN pip3 install --no-cache-dir \
    ultralytics \
    opencv-python-headless \
    paho-mqtt

# Kopírovanie Python skriptu do kontajnera
COPY yolo_camera.py /app/

# Nastavenie spustenia Python skriptu
# ENTRYPOINT ["python3", "/app/yolo_camera.py"]
