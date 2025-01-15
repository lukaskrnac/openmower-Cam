
# Použitie základného ROS obrazu (ROS Noetic na Ubuntu 20.04)
FROM ros:noetic-ros-core

# Nastavenie pracovného adresára
WORKDIR /app

# Aktualizácia systému a inštalácia potrebných balíkov
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-opencv \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Inštalácia Python knižníc cez pip
RUN pip3 install --no-cache-dir \
    ultralytics \
    opencv-python-headless \
    rospy \
    rospkg \
    catkin_pkg \
    cv_bridge \
    sensor-msgs \
    std-msgs

# Kopírovanie vášho Python skriptu do kontajnera
COPY yolo_camera_node.py /app/

# Nastavenie spustenia Python skriptu
CMD ["python3", "/app/yolo_camera_node.py"]
