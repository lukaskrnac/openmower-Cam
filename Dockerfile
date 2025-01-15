# Použitie ROS Noetic obrazu (založené na Ubuntu 20.04)
FROM ros:noetic-ros-core

# Nastavenie pracovného adresára
WORKDIR /app

# Aktualizácia systému a inštalácia ROS balíkov a systémových závislostí
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-opencv \
    ffmpeg \
    libsm6 \
    libxext6 \
    ros-noetic-rospy \
    ros-noetic-sensor-msgs \
    ros-noetic-std-msgs \
    ros-noetic-cv-bridge \
    ros-noetic-catkin && \
    apt-get autoremove -y && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Inštalácia Python knižníc cez pip
RUN pip3 install --no-cache-dir \
    ultralytics==8.0.20 \
    opencv-python-headless \
    rospkg

# Kopírovanie Python skriptu do kontajnera
COPY yolo_camera_node.py /app/

# Nastavenie spustenia Python skriptu
ENTRYPOINT ["python3", "/app/yolo_camera_node.py"]
