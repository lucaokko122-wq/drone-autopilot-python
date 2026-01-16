from dronekit_sitl import SITL
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import webbrowser


class AntiJammingDrone:
    def __init__(self):
        self.sitl = None
        self.vehicle = None
        self.connection_string = "tcp:127.0.0.1:5760"
        self.map_file = "drone_map.html"

    def create_map(self):
        """Создать карту с маркером дрона"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>БПЛА Симулятор</title>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                #map { height: 600px; width: 800px; margin: 20px auto; border: 2px solid #333; }
                body { font-family: Arial; text-align: center; }
            </style>
        </head>
        <body>
            <h2>Карта полета БПЛА</h2>
            <div id="map"></div>

            <script>
                var map = L.map('map').setView([34.052235, -118.243683], 13);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

                var droneIcon = L.icon({
                    iconUrl: 'https://cdn-icons-png.flaticon.com/512/824/824100.png',
                    iconSize: [40, 40]
                });

                var marker = L.marker([34.052235, -118.243683], {icon: droneIcon}).addTo(map);

                function updatePosition(lat, lon) {
                    marker.setLatLng([lat, lon]);
                    map.panTo([lat, lon]);
                }

                // Демо движение
                var demoLat = 34.052235;
                setInterval(function() {
                    demoLat += 0.0001;
                    updatePosition(demoLat, -118.243683);
                }, 1000);
            </script>
        </body>
        </html>"""

        with open(self.map_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"Карта создана: {self.map_file}")
        try:
            webbrowser.open(self.map_file)
        except:
            print("Открой файл drone_map.html в браузере")

    def start_simulation(self):
        print("=== ЗАПУСК СИМУЛЯЦИИ ===")

        try:
            print("1. Инициализация SITL...")
            self.sitl = SITL()

            print("2. Скачивание симулятора...")
            self.sitl.download('copter', '3.3', verbose=False)

            print("3. Запуск симулятора...")
            self.sitl.launch(
                ['--home=34.052235,-118.243683,0,0'],
                await_ready=True,
                restart=True
            )

            print(f"4. Подключение к {self.connection_string}...")
            self.vehicle = connect(
                self.connection_string,
                wait_ready=True,
                timeout=30
            )

            print(f"5. Подключено!")
            print(f"   Режим: {self.vehicle.mode.name}")

            # Создаем карту
            self.create_map()

            return True

        except Exception as e:
            print(f"Ошибка: {e}")
            return False

    def simple_flight(self):
        print("\n=== ТЕСТОВЫЙ ПОЛЕТ ===")

        try:
            print("1. Ожидание готовности...")
            while not self.vehicle.is_armable:
                print(f"   GPS: {self.vehicle.gps_0.fix_type if hasattr(self.vehicle, 'gps_0') else 'N/A'}")
                time.sleep(1)

            print("2. GUIDED режим...")
            self.vehicle.mode = VehicleMode("GUIDED")
            time.sleep(2)

            print("3. Арминг...")
            self.vehicle.armed = True
            while not self.vehicle.armed:
                time.sleep(0.5)

            print("4. Взлет на 10м...")
            self.vehicle.simple_takeoff(10)

            for i in range(30):
                alt = self.vehicle.location.global_relative_frame.alt
                print(f"   Высота: {alt:.1f}м")
                if alt >= 9:
                    break
                time.sleep(1)

            print("5. Полет к точке...")
            target = LocationGlobalRelative(34.054235, -118.245683, 10)
            self.vehicle.simple_goto(target)
            time.sleep(10)

            print("6. Посадка...")
            self.vehicle.mode = VehicleMode("LAND")

            while self.vehicle.armed:
                alt = self.vehicle.location.global_relative_frame.alt
                print(f"   Высота: {alt:.1f}м")
                if alt < 0.5:
                    break
                time.sleep(1)

            print("Полет завершен!")
            return True

        except Exception as e:
            print(f"Ошибка полета: {e}")
            return False

    def cleanup(self):
        if self.vehicle:
            try:
                self.vehicle.close()
            except Exception:
                pass
        if self.sitl:
            try:
                self.sitl.stop()
            except Exception:
                pass


def main():
    print("АНТИГЛУШАЩИЙ БПЛА С КАРТОЙ")
    print("=" * 50)

    drone = AntiJammingDrone()

    try:
        if drone.start_simulation():
            print("\nСИМУЛЯЦИЯ ЗАПУЩЕНА")
            print("Карта открывается в браузере...")

            # Даем время открыть карту
            time.sleep(3)

            # Запускаем полет
            drone.simple_flight()

            print("\nНажмите Ctrl+C для выхода")
            while True:
                if drone.vehicle:
                    alt = drone.vehicle.location.global_relative_frame.alt
                    mode = drone.vehicle.mode.name
                    lat = drone.vehicle.location.global_relative_frame.lat
                    lon = drone.vehicle.location.global_relative_frame.lon
                    print(f"Координаты: {lat:.5f}, {lon:.5f} | Высота: {alt:.1f}м", end='\r')
                time.sleep(1)

        else:
            print("Не удалось запустить симуляцию")

    except KeyboardInterrupt:
        print("\n\nПрервано")
    finally:
        drone.cleanup()
        print("\nПрограмма завершена")


if __name__ == "__main__":
    main()