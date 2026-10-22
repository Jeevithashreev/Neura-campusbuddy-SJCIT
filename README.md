# Neura CampusBuddy: SJCIT

AI-based campus energy saver. It detects empty rooms with lights on, warns, switches them off automatically, and shows the energy and money saved. Built for MIN-360, SJCIT Chikkaballapura.

## Team Neura
- Nukala Jyoshitha
- Jeevithashree V
- Akshitha G A
- Vanija Y M

## The problem
Lights, fans and AC are often left running in empty classrooms, and nobody tracks it. This idea makes that waste visible and fixes it automatically.

## How it works
1. A camera counts the people in a room (YOLO, no frames or faces are stored).
2. The count goes to the server.
3. The rules engine decides: empty for 10 s gives a warning, empty for 20 s switches the lights off (demo timing, adjustable).
4. The dashboard shows each room's status and the energy and rupees saved.

## Built so far
- Rules engine (warn, switch off, savings)
- Floor view with 5 simulated rooms
- Camera people counting with YOLO
- Satellite map of the SJCIT campus

## Planned
- MQTT messages over Wi-Fi (fake ESP32 sensor)
- Real SJCIT room and building names
- Admin AI copilot
- Greenest Block leaderboard

## Note on originality
The idea builds on a concept we explored in an earlier hackathon. All code in this repository was written fresh for MIN-360.

## Run it
```
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn main:app
```
Open http://127.0.0.1:8000

Camera (second terminal):
```
python vision_yolo.py --room 2
```

## Tech
Python, FastAPI, OpenCV, YOLO (ultralytics), Leaflet.

Energy savings are simulated (assumption: Rs 8 per kWh).