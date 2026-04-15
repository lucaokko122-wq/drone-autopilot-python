# Autonomous UAV Guardian 🛸

An autonomous UAV control system with an integrated friend-or-foe recognition module and real-time telemetry visualization.

---

## 📌 Project Overview

This project is a software system designed for fully autonomous drone operation.
The UAV performs takeoff, area patrol, ground object analysis, and tactical decision-making (reporting or simulated strike) without human intervention.

---

## 🚀 Key Features

### Virtual Simulation

Uses `dronekit-sitl` to fully simulate flight physics and GPS behavior without requiring a physical drone.

### Autonomous Logic

Implements a full autonomous cycle:
**system checks (arming) → takeoff → patrol → landing**

### AI Decision Engine

Simulates a computer vision system to classify targets as **"friendly"** or **"hostile"** based on confidence scores.

### HQ Dashboard

Generates an HTML-based flight map and visual reports (`drone_view.png`) for mission monitoring.

### DevOps Logging

Detailed logging of all events and commands into `mission_log.txt`.

---

## 🛠 Tech Stack

* **Python 3.x** — core development language
* **DroneKit** — communication with flight controller via MAVLink
* **ArduPilot SITL** — simulation environment
* **Pillow (PIL)** — image generation and visualization
* **Leaflet.js** — interactive map rendering

---

## ⚙️ How to Run

### 1. Install dependencies

```bash
pip install dronekit dronekit-sitl Pillow
```

### 2. Run the project

```bash
python unified_autopilot.py
```

### 3. Monitoring

* Open `hq_map.html` to track UAV position
* Check `drone_view.png` for AI output

---

## 📂 Project Structure

* `unified_autopilot.py` — main system core
* `mission_log.txt` — telemetry and logs
* `drone_view.png` — latest recognition frame

---

## ⚠️ Disclaimer

This project was developed for educational purposes to demonstrate autonomous control principles and UAV software architecture.

