# PX4-ROS2-Gazebo-YOLOv8
Обнаружение объектов с воздуха с помощью дрона на базе PX4 Autopilot и ROS 2. Для симуляции используется PX4 SITL и Gazebo Harmonic. YOLOv8 применяется для обнаружения объектов.

## Демо
https://github.com/monemati/PX4-ROS2-Gazebo-YOLOv8/assets/58460889/fab19f49-0be6-43ea-a4e4-8e9bc8d59af9

## Установка (нативно, без Docker)
Проект протестирован на **Ubuntu 24.04 LTS (Noble)** с ROS 2 Jazzy и Gazebo Harmonic. Используйте PX4-Autopilot v1.15.0.

### Создайте виртуальное окружение
```commandline
# Создать
python3 -m venv ~/px4-venv

# Активировать (в каждом терминале)
source ~/px4-venv/bin/activate
```

### Клонируйте репозиторий
```commandline
git clone https://github.com/monemati/PX4-ROS2-Gazebo-YOLOv8.git
cd PX4-ROS2-Gazebo-YOLOv8
```

### Установите PX4-Autopilot (v1.15.0)
```commandline
cd ~
git clone https://github.com/PX4/PX4-Autopilot.git --recursive -b v1.15.0
cd PX4-Autopilot
bash ./Tools/setup/ubuntu.sh  # Установит зависимости, включая Gazebo Harmonic
make px4_sitl  # Сборка SITL
```

### Установите ROS 2 Jazzy
```commandline
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu noble main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt update && sudo apt upgrade -y
sudo apt install ros-jazzy-desktop ros-jazzy-ros-gz-bridge ros-dev-tools
source /opt/ros/jazzy/setup.bash && echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
pip install --user -U empy pyros-genmsg setuptools
```

### Установите Micro XRCE-DDS Agent
```commandline
cd ~
git clone https://github.com/eProsima/Micro-XRCE-DDS-Agent.git
cd Micro-XRCE-DDS-Agent
mkdir build && cd build
cmake ..
make
sudo make install
sudo ldconfig /usr/local/lib/
```

### Установите MAVSDK и YOLOv8
```commandline
source ~/px4-venv/bin/activate
pip install mavsdk aioconsole pygame "numpy==1.26.4" "opencv-python==4.9.0.80" ultralytics
```

### Дополнительные конфиги
- Добавьте в `~/.bashrc`:
```commandline
source /opt/ros/jazzy/setup.bash
export GZ_SIM_RESOURCE_PATH=~/PX4-Autopilot/Tools/simulation/gz/models  # Для моделей Gazebo Harmonic
export GZ_SIM_WORLD_PATH=~/PX4-Autopilot/Tools/simulation/gz/worlds
```
  Затем: `source ~/.bashrc`

- Скопируйте модели:
```commandline
cp -r ~/PX4-ROS2-Gazebo-YOLOv8/models/* ~/PX4-Autopilot/Tools/simulation/gz/models
```

- Скопируйте мир:
```commandline
cp ~/PX4-ROS2-Gazebo-YOLOv8/worlds/default.sdf ~/PX4-Autopilot/Tools/simulation/gz/worlds/
```

- Измените угол камеры дрона (для лучшего обзора):
  Откройте `~/PX4-Autopilot/Tools/simulation/gz/models/x500_vision/model.sdf` (или x500_depth), найдите `<pose>` в строке с камерой и замените на:
```xml
<pose>0.15 0.029 0.21 0 0.7854 0</pose>
```
  Пересоберите PX4: `cd ~/PX4-Autopilot && make px4_sitl`.


## Запуск
Используйте **модель `x500_vision`** (airframe 4001) или `x500_depth` (4002) с RGB-камерой.

### Полёт с клавиатуры
Откройте 5 терминалов. Активируйте venv где нужно: `source ~/px4-venv/bin/activate`.

```commandline
# Терминал 1: Agent
cd ~/Micro-XRCE-DDS-Agent/build
./MicroXRCEAgent udp4 -p 8888

# Терминал 2: PX4 + Gazebo (пример для x500_depth)
cd ~/PX4-Autopilot
PX4_SYS_AUTOSTART=4001 PX4_GZ_MODEL_POSE="268.08,-128.22,3.86,0.00,0,-0.7" PX4_GZ_MODEL=x500_depth make px4_sitl gz_x500_depth

# Терминал 3: Bridge для камеры
ros2 run ros_gz_bridge parameter_bridge /camera@sensor_msgs/msg/Image@gz.msgs.Image

# Терминал 4: YOLO-детекция
cd ~/PX4-ROS2-Gazebo-YOLOv8
python uav_camera_det.py  # Или упрощённая версия без cv_bridge

# Терминал 5: Управление клавиатурой
cd ~/PX4-ROS2-Gazebo-YOLOv8
python keyboard-mavsdk-test.py
```
- Кликните на пустое окно клавиатуры.
- `r` — взлёт и arm.
- WASD / стрелки — движение.
- `l` — посадка.

### Полёт через ROS 2 (offboard)
Аналогично, но в Терминале 5:
```commandline
# Сначала соберите ws_offboard_control (если нужно, клонируйте px4_ros_com и px4_msgs в ~/ws_offboard_control/src, colcon build)
cd ~/ws_offboard_control
source install/local_setup.bash
ros2 run px4_ros_com offboard_control
```
(Поза: измените на "283.08,-136.22,3.86,0.00,0,-0.7" для избежания столкновений.)

## Благодарности
- https://github.com/PX4/PX4-Autopilot
- https://github.com/ultralytics/ultralytics
- https://www.ros.org/
- https://gazebosim.org/