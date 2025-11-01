import asyncio
import random
from mavsdk import System
import KeyPressModule as kp

# Модуль KeyPressModule используется для отслеживания нажатий клавиш

kp.init()
drone = System()

# Начальные значения управления: крен (roll), тангаж (pitch), газ (throttle), рысканье (yaw)
roll, pitch, throttle, yaw = 0, 0, 0.5, 0

# Асинхронная функция для получения ввода с клавиатуры
async def getKeyboardInput(my_drone):
    global roll, pitch, throttle, yaw
    while True:
        roll, pitch, throttle, yaw = 0, 0, 0.5, 0
        value = 0.5
        # Управление направлением
        if kp.getKey("LEFT"):
            pitch = -value     # Вперёд/назад (наклон вперёд)
        elif kp.getKey("RIGHT"):
            pitch = value
        if kp.getKey("UP"):
            roll = value       # Влево/вправо (наклон влево)
        elif kp.getKey("DOWN"):
            roll = -value
        # Газ (высота)
        if kp.getKey("w"):
            throttle = 1       # Вверх
        elif kp.getKey("s"):
            throttle = 0       # Вниз
        # Повороты
        if kp.getKey("a"):
            yaw = -value       # Влево
        elif kp.getKey("d"):
            yaw = value        # Вправо
        # Печать текущего режима полёта
        elif kp.getKey("i"):
            asyncio.ensure_future(print_flight_mode(my_drone))
        # Армирование (включение моторов)
        elif kp.getKey("r") and my_drone.telemetry.landed_state():
            await my_drone.action.arm()
        # Посадка
        elif kp.getKey("l") and my_drone.telemetry.in_air():
            await my_drone.action.land()

        await asyncio.sleep(0.1)

# Асинхронная функция для вывода текущего режима полёта
async def print_flight_mode(my_drone):
    async for flight_mode in my_drone.telemetry.flight_mode():
        print("FlightMode:", flight_mode)

# Асинхронное управление дроном вручную
async def manual_control_drone(my_drone):
    global roll, pitch, throttle, yaw
    while True:
        print(roll, pitch, throttle, yaw)
        await my_drone.manual_control.set_manual_control_input(roll, pitch, throttle, yaw)
        await asyncio.sleep(0.1)

# Основная функция запуска дрона
async def run_drone():
    asyncio.ensure_future(getKeyboardInput(drone))
    await drone.connect(system_address="udp://0.0.0.0:14540")
    print("Ожидание подключения дрона...")

    # Ожидание подключения
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("-- Подключение к дрону установлено!")
            break

    # Проверка GPS и домашней позиции
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Позиция и состояние GPS достаточно точные для полёта.")
            break

    asyncio.ensure_future(manual_control_drone(drone))

# Запуск асинхронных задач
async def run():
    global roll, pitch, throttle, yaw
    await asyncio.gather(run_drone())

if __name__ == "__main__":
    # Запуск основного цикла
    asyncio.ensure_future(run())
    asyncio.get_event_loop().run_forever()
