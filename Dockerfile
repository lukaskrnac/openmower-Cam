# Použitie ROS Noetic obrazu (založené na Ubuntu 20.04)
FROM benchpilot/raspbian-picamera2:server

# Nastavenie pracovného adresára
WORKDIR /app

# Aktualizácia systému balíkov a systémových závislostí
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip

# Inštalácia Python knižníc cez pip
RUN pip3 install --no-cache-dir \
    ultralytics \
    opencv-python-headless \
    paho-mqtt

# Kopírovanie Python skriptu do kontajnera
COPY yolo_camera.py /app/

# Nastavenie spustenia Python skriptu
ENTRYPOINT ["python3", "/app/yolo_camera.py"]
