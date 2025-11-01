# Базовая программа ROS 2 для подписки на потоковое видео 
# с вашей встроенной веб-камеры в реальном времени
# Автор:
# - Addison Sears-Collins
# - https://automaticaddison.com

# Импорт необходимых библиотек
import rclpy                     # Библиотека Python для ROS 2
from rclpy.node import Node       # Класс для создания узлов (nodes)
from sensor_msgs.msg import Image # Тип сообщения ROS для изображений
from cv_bridge import CvBridge    # Конвертер между изображениями ROS и OpenCV
import cv2                        # Библиотека OpenCV
from ultralytics import YOLO      # Библиотека YOLO (детекция объектов)

# Загружаем модель YOLOv8 среднего размера
model = YOLO('yolov8m.pt')


class ImageSubscriber(Node):
    """
    Класс подписчика изображений — наследуется от класса Node.
    """
    def __init__(self):
        """
        Конструктор класса — настройка узла.
        """
        # Инициализация базового класса Node с именем узла
        super().__init__('image_subscriber')
        
        # Создаём подписчика. Он будет получать сообщения типа Image
        # из топика 'camera'. Очередь сообщений — 10.
        self.subscription = self.create_subscription(
            Image, 
            'camera', 
            self.listener_callback, 
            10)
        self.subscription  # предотвращает предупреждение об неиспользуемой переменной
        
        # Конвертер между изображениями ROS и OpenCV
        self.br = CvBridge()
   
    def listener_callback(self, data):
        """
        Функция обратного вызова (callback), вызывается при получении кадра.
        """
        # Выводим сообщение в консоль
        self.get_logger().info('Получен кадр видео')
 
        # Преобразуем изображение из формата ROS в формат OpenCV
        current_frame = self.br.imgmsg_to_cv2(data, desired_encoding="bgr8")
        image = current_frame

        # Детекция объектов при помощи YOLO
        # classes=[0, 2] — значит, модель ищет только объекты с классами 0 и 2 
        # (например, человек и автомобиль, в зависимости от обучающей модели)
        results = model.predict(image, classes=[0, 2])

        # Отрисовываем результаты детекции на изображении
        img = results[0].plot()

        # Изменяем размер окна для удобства отображения
        resized = cv2.resize(img, (960, 540))  # ширина=960, высота=540

        # Показываем изображение в окне
        cv2.imshow('Detected Frame', resized)
  
        # Обновляем окно (без этой строки окно зависнет)
        cv2.waitKey(1)
  

def main(args=None):
    """
    Основная функция — инициализация ROS 2 и запуск узла.
    """
    # Инициализация библиотеки rclpy
    rclpy.init(args=args)
  
    # Создаём экземпляр узла-подписчика
    image_subscriber = ImageSubscriber()
  
    # Поддерживаем работу узла — функция spin() удерживает его активным,
    # чтобы callback срабатывал при получении новых данных
    rclpy.spin(image_subscriber)
  
    # Уничтожаем узел (опционально)
    image_subscriber.destroy_node()
  
    # Завершаем работу библиотеки rclpy
    rclpy.shutdown()
  

# Точка входа в программу
if __name__ == '__main__':
    main()
