import time
import logging
import webbrowser
import random
from datetime import datetime
from dronekit import connect, VehicleMode, LocationGlobalRelative
from dronekit_sitl import SITL
from PIL import Image, ImageDraw, ImageFont

# ==================== СИСТЕМА ЛОГИРОВАНИЯ ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("mission_log.txt", encoding='utf-8'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


# ==================== МОДУЛЬ РАСПОЗНАВАНИЯ (AI SIMULATION) ====================
class CombatLogic:
    """Имитация системы распознавания целей и управления вооружением"""

    def __init__(self):
        self.friendly_ids = ["UAV-FRIENDLY-01", "BASE-ALPHA"]
        self.ammo_count = 5

    def scan_for_targets(self):
        """Симуляция работы нейросети: находит случайный объект"""
        targets = [
            {"id": "TRUCK-X", "type": "enemy", "confidence": 0.92},
            {"id": "UAV-FRIENDLY-01", "type": "friendly", "confidence": 0.98},
            {"id": "UNKNOWN-BUNKER", "type": "enemy", "confidence": 0.45},
            None  # Ничего не найдено
        ]
        return random.choice(targets)

    def decide_action(self, target):
        """Принятие решения на основе типа цели"""
        if not target:
            return "SEARCHING", "Целей не обнаружено."

        if target['type'] == 'friendly':
            return "IGNORE", f"Свой объект: {target['id']}. Огонь запрещен."

        if target['type'] == 'enemy':
            if target['confidence'] > 0.80:
                if self.ammo_count > 0:
                    self.ammo_count -= 1
                    return "STRIKE", f"ВРАГ: {target['id']}. Цель подтверждена. Удар нанесен!"
                return "REPORT", f"ВРАГ: {target['id']}. Нет БК. Передаю координаты в штаб."
            return "REPORT", f"Обнаружена подозрительная активность ({target['id']}). Нужно доразведка."


# ==================== ЯДРО УПРАВЛЕНИЯ БПЛА ====================
class AutonomousDrone:
    def __init__(self, name="SkyGuardian-01"):
        self.name = name
        self.sitl = None
        self.vehicle = None
        self.combat = CombatLogic()
        self.connection_string = "tcp:127.0.0.1:5760"

    def bootstrap(self):
        """Запуск SITL и подключение"""
        logger.info(f"--- ЗАПУСК СИСТЕМЫ {self.name} ---")
        try:
            self.sitl = SITL()
            self.sitl.download('copter', '3.3', verbose=False)
            # Точка старта: Москва
            self.sitl.launch(['--home=55.753395,37.625427,0,0'], await_ready=True, restart=True)
            self.vehicle = connect(self.connection_string, wait_ready=True, timeout=30)
            self._generate_map()
            return True
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
            return False

    def _generate_map(self):
        """Создание карты штаба"""
        html = f"<html><body style='margin:0;'><div id='map' style='height:100vh;'></div><script src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'></script><link rel='stylesheet' href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'/><script>var map = L.map('map').setView([55.753395, 37.625427], 17);L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);L.marker([55.753395, 37.625427]).addTo(map).bindPopup('{self.name}').openPopup();</script></body></html>"
        with open("hq_map.html", "w", encoding="utf-8") as f: f.write(html)
        webbrowser.open("hq_map.html")

    def run_mission(self):
        """Основной цикл автономной работы"""
        logger.info("Подготовка к взлету...")
        while not self.vehicle.is_armable:
            time.sleep(1)

        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True
        self.vehicle.simple_takeoff(20)  # Взлет на 20 метров

        # Цикл патрулирования и распознавания
        for i in range(5):  # 5 циклов сканирования
            alt = self.vehicle.location.global_relative_frame.alt
            logger.info(f"Патрулирование... Высота: {alt:.1f}м")

            # РАБОТА СИСТЕМЫ РАСПОЗНАВАНИЯ
            target = self.combat.scan_for_targets()
            action, message = self.combat.decide_action(target)

            if action == "STRIKE":
                logger.warning(f"!!! [БОЕВАЯ РАБОТА] {message}")
            elif action == "REPORT":
                logger.info(f">>> [ДОКЛАД В ШТАБ] {message}")
            else:
                logger.info(f"--- [СКАНИРОВАНИЕ] {message}")

            self._save_visual_report(action, target)
            time.sleep(4)

        logger.info("Миссия завершена. Возврат на базу.")
        self.vehicle.mode = VehicleMode("LAND")

    def _save_visual_report(self, action, target):
        """Создание визуального кадра 'глазами дрона'"""
        img = Image.new('RGB', (500, 300), color=(10, 10, 10))
        d = ImageDraw.Draw(img)
        color = (255, 255, 255)
        if action == "STRIKE": color = (255, 0, 0)
        if action == "IGNORE": color = (0, 255, 0)

        d.text((20, 20), f"OBJECT ID: {target['id'] if target else 'NONE'}", fill=color)
        d.text((20, 50), f"ACTION: {action}", fill=color)
        d.text((20, 80), f"CONFIDENCE: {target['confidence'] if target else 0.0}", fill=color)
        d.text((20, 250), f"TIME: {datetime.now().strftime('%H:%M:%S')}", fill=(100, 100, 100))
        img.save("drone_view.png")

    def shutdown(self):
        if self.vehicle: self.vehicle.close()
        if self.sitl: self.sitl.stop()
        logger.info("Система выключена.")


# ==================== ЗАПУСК ====================
if __name__ == "__main__":
    drone = AutonomousDrone()
    try:
        if drone.bootstrap():
            drone.run_mission()
    except KeyboardInterrupt:
        logger.warning("Прервано оператором.")
    finally:
        drone.shutdown()