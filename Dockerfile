# Použitie ROS Noetic obrazu (založené na Ubuntu 20.04)
FROM arm64v8/python:3.9.21-bullseye

# Nastavenie pracovného adresára
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg && \
    curl -fsSL https://archive.raspberrypi.org/debian/raspberrypi.gpg.key | \
    gpg --dearmor -o /usr/share/keyrings/raspberrypi-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/raspberrypi-archive-keyring.gpg] http://archive.raspberrypi.org/debian bullseye main" > /etc/apt/sources.list.d/raspi.list && \
    apt-get update && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
    
# Aktualizácia systému balíkov a systémových závislostí
RUN apt-get update && apt-get install \
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
