import logging
import sys
import time
from datetime import datetime
from enum import Enum
import os
from PIL import Image, ImageDraw, ImageFont


# ==================== НАСТРОЙКА ЛОГИРОВАНИЯ ====================
class DroneLogger:
    """Класс для логирования действий дронов"""

    def __init__(self, log_file="drone_log.txt"):
        self.log_file = log_file
        self.setup_logging()

    def setup_logging(self):
        """Настройка системы логирования"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def log_action(self, drone_name, action, result=""):
        """Записать действие в лог"""
        message = f"[{drone_name}] {action}"
        if result:
            message += f" -> {result}"
        self.logger.info(message)

    def log_error(self, drone_name, error_message):
        """Записать ошибку в лог"""
        self.logger.error(f"[{drone_name}] ОШИБКА: {error_message}")

    def log_warning(self, drone_name, warning_message):
        """Записать предупреждение в лог"""
        self.logger.warning(f"[{drone_name}] ПРЕДУПРЕЖДЕНИЕ: {warning_message}")


# ==================== ПЕРЕЧИСЛЕНИЕ КОМАНД ====================
class DroneCommand(Enum):
    """Команды управления дроном"""
    TAKEOFF = "takeoff"
    LAND = "land"
    EMERGENCY_LAND = "emergency"
    SET_WAYPOINTS = "waypoints"
    FLY_TO_WAYPOINT = "flyto"
    STATUS = "status"
    HELP = "help"
    EXIT = "exit"
    START_RECORDING = "record_start"
    STOP_RECORDING = "record_stop"
    LOCK_TARGET = "lock"
    FIRE = "fire"
    RELOAD = "reload"
    LOAD_CARGO = "load"
    UNLOAD_CARGO = "unload"


# ==================== БАЗОВЫЙ КЛАСС БПЛА ====================
class Bpla:
    """Базовый класс для всех типов БПЛА"""

    def __init__(self, name, team, max_altitude=100):
        self.name = name
        self.team = team
        self.max_altitude = max_altitude
        self.is_flying = False
        self.current_altitude = 0
        self.waypoints = []
        self.weapons = []
        self.sensors = []
        self.drone_type = "Базовый БПЛА"
        self.logger = DroneLogger()
        self.logger.log_action(self.name, f"Дрон создан: {team}, тип: {self.drone_type}")

    def takeoff(self, target_altitude=10):
        """Метод для взлета БПЛА"""
        if not self.is_flying:
            if target_altitude > self.max_altitude:
                msg = f"Ошибка: высота {target_altitude} превышает максимальную {self.max_altitude}"
                self.logger.log_error(self.name, msg)
                return msg
            self.is_flying = True
            self.current_altitude = target_altitude
            msg = f"Взлет на {target_altitude}м"
            self.logger.log_action(self.name, "Взлет", msg)
            return f"{self.name}: {msg}"
        else:
            msg = "Уже в воздухе"
            self.logger.log_warning(self.name, msg)
            return f"{self.name}: {msg}"

    def land(self):
        """Метод для посадки БПЛА"""
        if self.is_flying:
            self.is_flying = False
            self.current_altitude = 0
            msg = "Посадка выполнена"
            self.logger.log_action(self.name, "Посадка", msg)
            return f"{self.name}: {msg}"
        else:
            msg = "Уже на земле"
            self.logger.log_warning(self.name, msg)
            return f"{self.name}: {msg}"

    def emergency_land(self):
        """Аварийная посадка"""
        self.is_flying = False
        self.current_altitude = 0
        self.waypoints = []
        msg = "Аварийная посадка"
        self.logger.log_action(self.name, "Аварийная посадка", "Все системы остановлены")
        return f"{self.name}: {msg}"

    def set_waypoints(self, points):
        """Установка точек маршрута"""
        self.waypoints = points
        msg = f"Установлено {len(points)} точек маршрута"
        self.logger.log_action(self.name, "Установка точек маршрута", msg)
        return f"{self.name}: {msg}"

    def fly_to_waypoint(self, waypoint_index):
        """Полет к конкретной точке маршрута"""
        if not self.is_flying:
            msg = "Не может лететь - не в воздухе"
            self.logger.log_error(self.name, msg)
            return f"{self.name}: {msg}"
        if waypoint_index >= len(self.waypoints):
            msg = f"Точки с индексом {waypoint_index} не существует"
            self.logger.log_error(self.name, msg)
            return f"{self.name}: {msg}"
        target = self.waypoints[waypoint_index]
        msg = f"Летит к точке {target}"
        self.logger.log_action(self.name, f"Полет к точке {waypoint_index}", msg)
        return f"{self.name}: {msg}"

    def get_status(self):
        """Получить статус дрона"""
        status = "В воздухе" if self.is_flying else "На земле"
        return f"""
{self.name} ({self.drone_type})
Команда: {self.team}
Статус: {status}
Высота: {self.current_altitude}м / Макс: {self.max_altitude}м
Точек маршрута: {len(self.waypoints)}
        """

    def generate_status_image(self, filename="drone_status.png"):
        """Создать изображение со статусом дрона"""
        try:
            width, height = 600, 400
            image = Image.new('RGB', (width, height), color='black')
            draw = ImageDraw.Draw(image)

            try:
                font = ImageFont.truetype("arial.ttf", 20)
                title_font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
                title_font = ImageFont.load_default()

            title = f"СТАТУС БПЛА: {self.name}"
            draw.text((50, 30), title, fill='yellow', font=title_font)

            status_color = 'green' if self.is_flying else 'red'
            status_text = f"Статус: {'В ПОЛЕТЕ' if self.is_flying else 'НА ЗЕМЛЕ'}"
            draw.text((50, 80), status_text, fill=status_color, font=font)
            draw.text((50, 110), f"Высота: {self.current_altitude} м", fill='cyan', font=font)
            draw.text((50, 140), f"Макс. высота: {self.max_altitude} м", fill='lightblue', font=font)
            draw.text((50, 170), f"Точек маршрута: {len(self.waypoints)}", fill='orange', font=font)
            draw.text((50, 200), f"Команда: {self.team}", fill='magenta', font=font)
            draw.text((50, 230), f"Тип: {self.drone_type}", fill='white', font=font)

            if self.is_flying:
                draw.ellipse((400, 100, 500, 150), fill='gray', outline='white')
                draw.line((450, 150, 450, 200), fill='white', width=3)
                draw.ellipse((425, 200, 475, 210), fill='red')
            else:
                draw.ellipse((400, 250, 500, 300), fill='gray', outline='white')
                draw.line((450, 250, 450, 200), fill='white', width=3)

            image.save(filename)
            self.logger.log_action(self.name, "Создание изображения статуса", filename)

            try:
                image.show()
            except:
                pass

            return filename

        except Exception as e:
            self.logger.log_error(self.name, f"Ошибка создания изображения: {e}")
            return None

    # ==================== DRONEKIT ИНТЕГРАЦИЯ (ЗАГЛУШКИ) ====================
    def connect_to_dronekit(self, connection_string="tcp:127.0.0.1:5760"):
        """Подключение к реальному дрону через DroneKit"""
        self.logger.log_action(self.name, "Попытка подключения к DroneKit", connection_string)

        # Заглушка для реальной интеграции
        # В реальности здесь будет:
        # from dronekit import connect
        # self.vehicle = connect(connection_string, wait_ready=True)

        return f"{self.name}: Подключение к DroneKit симулятору ({connection_string})"

    def get_dronekit_status(self):
        """Получение статуса из DroneKit"""
        if hasattr(self, 'vehicle'):
            # Реальная интеграция с DroneKit
            # return f"Реальный статус: {self.vehicle.location.global_relative_frame.alt}"
            pass
        return f"{self.name}: Используется симуляция DroneKit"

    def send_mavlink_command(self, command):
        """Отправка MAVLink команды"""
        self.logger.log_action(self.name, "Отправка MAVLink команды", command)
        # Реальная интеграция с MAVLink
        return f"{self.name}: MAVLink команда отправлена: {command}"


# ==================== СПЕЦИАЛИЗИРОВАННЫЕ КЛАССЫ ====================
class ReconDrone(Bpla):
    """Класс разведывательного БПЛА"""

    def __init__(self, name, team, camera_resolution="4K"):
        super().__init__(name, team, max_altitude=50)
        self.drone_type = "Разведывательный БПЛА"
        self.camera_resolution = camera_resolution
        self.sensors.append("Камера высокого разрешения")
        self.sensors.append("Тепловизор")
        self.is_recording = False
        self.logger.log_action(self.name, f"Разведчик создан, камера: {camera_resolution}")

    def start_recording(self):
        """Начать запись видео"""
        if self.is_flying:
            self.is_recording = True
            msg = f"Запись начата в {self.camera_resolution}"
            self.logger.log_action(self.name, "Старт записи", msg)
            return f"{self.name}: {msg}"
        msg = "Не могу записывать - дрон не в воздухе"
        self.logger.log_error(self.name, msg)
        return f"{self.name}: {msg}"

    def stop_recording(self):
        """Остановить запись"""
        self.is_recording = False
        msg = "Запись остановлена"
        self.logger.log_action(self.name, "Стоп записи", msg)
        return f"{self.name}: {msg}"

    def get_status(self):
        base_status = super().get_status()
        recording = "Идет запись" if self.is_recording else "Запись остановлена"
        return base_status + f"Камера: {self.camera_resolution}\nЗапись: {recording}\n"


class CombatDrone(Bpla):
    """Класс боевого БПЛА"""

    def __init__(self, name, team, weapon_type="ракеты"):
        super().__init__(name, team, max_altitude=200)
        self.drone_type = "Боевой БПЛА"
        self.weapon_type = weapon_type
        self.weapons.append(weapon_type)
        self.weapons.append("пулемет")
        self.ammo = 100
        self.target_locked = False
        self.logger.log_action(self.name, f"Боевой дрон создан, оружие: {weapon_type}")

    def lock_target(self, target_name):
        """Захватить цель"""
        self.target_locked = True
        msg = f"Цель захвачена: {target_name}"
        self.logger.log_action(self.name, "Захват цели", msg)
        return f"{self.name}: {msg}"

    def fire(self):
        """Произвести выстрел"""
        if not self.target_locked:
            msg = "Нет захваченной цели!"
            self.logger.log_error(self.name, msg)
            return f"{self.name}: {msg}"
        if self.ammo <= 0:
            msg = "Боеприпасы закончились!"
            self.logger.log_error(self.name, msg)
            return f"{self.name}: {msg}"

        self.ammo -= 1
        msg = f"Выстрел {self.weapon_type}! Осталось: {self.ammo}"
        self.logger.log_action(self.name, "Выстрел", msg)
        return f"{self.name}: {msg}"

    def reload(self):
        """Перезарядка"""
        self.ammo = 100
        msg = "Перезарядка завершена"
        self.logger.log_action(self.name, "Перезарядка", msg)
        return f"{self.name}: {msg}"

    def get_status(self):
        base_status = super().get_status()
        target = "Цель захвачена" if self.target_locked else "Цель не захвачена"
        return base_status + f"Оружие: {self.weapon_type}\n{target}\nБоеприпасы: {self.ammo}\n"


# ==================== ИНТЕРАКТИВНОЕ УПРАВЛЕНИЕ ====================
class DroneController:
    """Класс для интерактивного управления дронами с клавиатуры"""

    def __init__(self):
        self.drones = []
        self.current_drone = None
        self.running = True
        self.logger = DroneLogger()

    def add_drone(self, drone):
        """Добавить дрон в контроллер"""
        self.drones.append(drone)
        self.logger.log_action("Controller", f"Дрон добавлен: {drone.name}")

    def select_drone(self):
        """Выбор дрона для управления"""
        if not self.drones:
            print("Нет доступных дронов")
            return None

        print("\n=== ВЫБОР ДРОНА ===")
        for i, drone in enumerate(self.drones, 1):
            print(f"{i}. {drone.name} ({drone.drone_type})")

        try:
            choice = int(input("Выберите дрон (номер): ")) - 1
            if 0 <= choice < len(self.drones):
                self.current_drone = self.drones[choice]
                print(f"Выбран дрон: {self.current_drone.name}")
                return self.current_drone
            else:
                print("Неверный выбор")
                return None
        except ValueError:
            print("Введите число")
            return None

    def show_menu(self):
        """Показать меню управления"""
        print("\n" + "=" * 50)
        print("СИСТЕМА УПРАВЛЕНИЯ БПЛА")
        print("=" * 50)

        if self.current_drone:
            print(f"Текущий дрон: {self.current_drone.name} ({self.current_drone.drone_type})")
            print("-" * 30)

        print("1. Выбрать дрон")
        print("2. Взлет (t)")
        print("3. Посадка (l)")
        print("4. Аварийная посадка (e)")
        print("5. Установить точки маршрута (w)")
        print("6. Полет к точке (f)")
        print("7. Статус (s)")
        print("8. Показать изображение статуса (i)")
        print("9. DroneKit подключение (d)")

        if isinstance(self.current_drone, ReconDrone):
            print("10. Начать запись (r)")
            print("11. Остановить запись (x)")
        elif isinstance(self.current_drone, CombatDrone):
            print("10. Захватить цель (c)")
            print("11. Выстрел (g)")
            print("12. Перезарядка (p)")

        print("0. Выход (q)")
        print("=" * 50)

    def handle_command(self, command):
        """Обработка команд с клавиатуры"""
        if not self.current_drone:
            print("Сначала выберите дрон!")
            return

        command = command.lower().strip()

        # Базовые команды
        if command in ['t', '2', 'takeoff']:
            try:
                altitude = float(input("Высота взлета (м): "))
                print(self.current_drone.takeoff(altitude))
            except ValueError:
                print("Введите число")

        elif command in ['l', '3', 'land']:
            print(self.current_drone.land())

        elif command in ['e', '4', 'emergency']:
            print(self.current_drone.emergency_land())

        elif command in ['w', '5', 'waypoints']:
            points = []
            print("Введите точки маршрута (x,y). Пустая строка - завершить")
            while True:
                point = input("Точка (x,y): ").strip()
                if not point:
                    break
                try:
                    x, y = map(float, point.split(','))
                    points.append((x, y))
                except:
                    print("Формат: число,число")
            if points:
                print(self.current_drone.set_waypoints(points))

        elif command in ['f', '6', 'flyto']:
            try:
                index = int(input("Индекс точки: "))
                print(self.current_drone.fly_to_waypoint(index))
            except ValueError:
                print("Введите число")

        elif command in ['s', '7', 'status']:
            print(self.current_drone.get_status())

        elif command in ['i', '8', 'image']:
            filename = input("Имя файла изображения (по умолчанию drone_status.png): ").strip()
            if not filename:
                filename = f"{self.current_drone.name.lower()}_status.png"
            self.current_drone.generate_status_image(filename)

        elif command in ['d', '9', 'dronekit']:
            conn = input("Строка подключения (по умолчанию tcp:127.0.0.1:5760): ").strip()
            if not conn:
                conn = "tcp:127.0.0.1:5760"
            print(self.current_drone.connect_to_dronekit(conn))

        # Команды для разведчика
        elif command in ['r', '10', 'record'] and isinstance(self.current_drone, ReconDrone):
            print(self.current_drone.start_recording())

        elif command in ['x', '11', 'stop'] and isinstance(self.current_drone, ReconDrone):
            print(self.current_drone.stop_recording())

        # Команды для боевого дрона
        elif command in ['c', '10', 'lock'] and isinstance(self.current_drone, CombatDrone):
            target = input("Имя цели: ").strip()
            print(self.current_drone.lock_target(target))

        elif command in ['g', '11', 'fire'] and isinstance(self.current_drone, CombatDrone):
            print(self.current_drone.fire())

        elif command in ['p', '12', 'reload'] and isinstance(self.current_drone, CombatDrone):
            print(self.current_drone.reload())

        elif command in ['1']:
            self.select_drone()

        elif command in ['q', '0', 'exit', 'quit']:
            print("Завершение работы...")
            self.running = False

        else:
            print("Неизвестная команда. Используйте меню.")

    def run(self):
        """Запуск интерактивного управления"""
        print("Инициализация системы управления БПЛА...")

        # Создаем тестовые дроны
        recon = ReconDrone("Орёл-1", "Разведка", "8K")
        combat = CombatDrone("Сокол-1", "Штурм", "управляемые ракеты")
        cargo = Bpla("Вепрь-1", "Логистика", 30)

        self.add_drone(recon)
        self.add_drone(combat)
        self.add_drone(cargo)

        # Автовыбор первого дрона
        self.current_drone = self.drones[0]

        print(f"Система готова. Выбран дрон: {self.current_drone.name}")
        print("Логирование ведется в файл: drone_log.txt")

        # Основной цикл управления
        while self.running:
            self.show_menu()
            command = input("Команда: ").strip()
            self.handle_command(command)
            time.sleep(0.5)  # Небольшая пауза для читаемости

        print("Система управления завершена.")
        print(f"Лог сохранен в: drone_log.txt")


# ==================== ОСНОВНАЯ ПРОГРАММА ====================
def main():
    """Основная функция программы"""
    print("=" * 60)
    print("СИСТЕМА УПРАВЛЕНИЯ БЕСПИЛОТНЫМИ ЛЕТАТЕЛЬНЫМИ АППАРАТАМИ")
    print("Версия 1.0")
    print("=" * 60)

    # Создаем и запускаем контроллер
    controller = DroneController()

    try:
        controller.run()
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем.")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
    finally:
        print("Работа программы завершена.")


if __name__ == "__main__":
    main()