Autonomous UAV Guardian 🛸

An autonomous UAV control system with an integrated friend-or-foe recognition module and real-time telemetry visualization.

📌 Project Overview

This project is a software system designed for fully autonomous drone operation.
The UAV performs takeoff, area patrol, ground object analysis, and tactical decision-making (reporting or simulated strike) without human intervention.

🚀 Key Features
Virtual Simulation
Uses dronekit-sitl to fully simulate flight physics and GPS behavior without requiring a physical drone.
Autonomous Logic
Implements a full autonomous cycle: system checks (arming) → takeoff → patrol → landing.
AI Decision Engine
Simulates a computer vision system to classify targets as "friendly" or "hostile" based on confidence scores.
HQ Dashboard
Generates an HTML-based flight map and visual reports (drone_view.png) for mission monitoring.
DevOps Logging
Detailed logging of all events and commands into mission_log.txt.
🛠 Tech Stack
Python 3.x — core development language
DroneKit — API for communication with the flight controller via MAVLink
ArduPilot SITL — simulation environment for testing
Pillow (PIL) — image generation and visualization
Leaflet.js — interactive map rendering in the browser
⚙️ How to Run
Install dependencies
pip install dronekit dronekit-sitl Pillow
Run the main script
python unified_autopilot.py
Monitoring
Open hq_map.html to track the UAV position
Check drone_view.png for simulated AI vision output
📂 Project Structure
unified_autopilot.py — main executable (core system)
mission_log.txt — telemetry and event log
drone_view.png — latest frame from the target recognition system
⚠️ Disclaimer

This project was developed for educational purposes to demonstrate autonomous control principles and UAV software architecture.
