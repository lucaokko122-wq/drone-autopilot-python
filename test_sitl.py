from dronekit_sitl import SITL
import time

print("===TEST SIMULATION SITL===")

try:
    sitl = SITL()
    print("1 Installing simulation")
    sitl.download('copter', '3.3', verbose=True)

    print("2 Start Simulation")
    sitl.launch([], await_ready=True, restart=True)

    print(f"3 simulation active: {sitl.connection_string()}")
    print("4. Симулятор работает 120 секунд...")

    time.sleep(120)

    print("5 Stop Simulation")
    sitl.stop()
    print("6 Test complete")

except Exception as e:
    print(f"ERROR: {e}")

sitl = SITL()
sitl.download('copter', '3.3')
sitl.launch([
    '--model', 'quad',
    '--home', '55.753395,37.625427,0,0',  # Москва, Красная площадь
    '--speedup', '1'
], await_ready=True)