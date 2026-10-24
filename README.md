# Neura CampusBuddy: SJCIT

AI-based campus energy saver and campus guide. It detects empty rooms with lights on, warns, switches them off automatically, and shows the energy and money saved for each block. Built for MIN-360 at SJCIT, Chikkaballapur.

## Team Neura
- Nukala Jyoshitha
- Jeevithashree V
- Akshitha G A
- Vanija Y M

## The problem
Lights and fans are often left running in empty classrooms, and nobody tracks the waste. CampusBuddy makes that waste visible and fixes it automatically.

## How it works
1. A camera counts the people in a room (YOLO). No frames or faces are stored, only a number is sent.
2. The count goes to the server. A sensor script can send counts for other blocks the same way a real room sensor would over Wi-Fi.
3. The rules engine decides: empty for 10 s gives a warning, empty for 20 s switches the lights off (demo timing, adjustable).
4. The dashboard, satellite map and leaderboard show each block's status and the energy and rupees saved.

## What is built
- Rules engine: warning, auto switch-off and savings for each block
- Dashboard with live status for 5 SJCIT blocks: Admin Block, IT Block, Library, Mechanical Block, Aeronautical Dept
- Live camera people counting with YOLO (camera is on one IT Block room)
- Fake room sensor (sensor.py) that sends occupancy to the server over the network
- Satellite map of the real campus, with block positions taken from Google Maps
- Greenest Block leaderboard (ranked by energy saved)
- Admin AI copilot (Gemini) that answers questions from the live data
- Student and Admin modes with a menu
- Events: register and give feedback
- Admin inbox: create events, read feedback, resolve problem reports
- Report a problem on the map
- Campus guide: search a place and a robot walks to it on the map

## Honest limits
- The camera is live on one IT Block room. The other blocks are simulated.
- Energy savings are estimates: we assume 420 W per block (6 tube lights and 4 fans) and Rs 8 per kWh. They are not measured.
- Demo timing is sped up (1 real second counts as 60 seconds).
- The guide robot walks in a straight line, not along real paths.
- The sign-in is a demo with no passwords.

## Planned
- MQTT messages for a real hardware pilot with room sensors
- Real room counts and electricity data for each block
- 3D campus map

## Note on originality
The idea builds on a concept we explored in an earlier hackathon. All code in this repository was written fresh for MIN-360, in a new repository.

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

Fake sensor (example: tells the server the Library is empty):
```
python sensor.py 3 0
```

AI copilot: create a file named `.env` with `GEMINI_API_KEY=your-key`. The key is kept out of GitHub.

## Tech
Python, FastAPI, OpenCV, YOLO (ultralytics), Leaflet, Gemini API.