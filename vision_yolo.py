"""CampusBuddy Step 2b: YOLO counts people and sends the number to the API.
Nothing is saved: frames are used in memory and thrown away."""
import argparse
import json
import time
import urllib.request
from collections import deque

import cv2
from ultralytics import YOLO

parser = argparse.ArgumentParser()
parser.add_argument("--room", type=int, default=2, help="room id this camera watches")
parser.add_argument("--source", default="0", help="0 for webcam, or a video file path")
parser.add_argument("--api", default="http://127.0.0.1:8000")
parser.add_argument("--conf", type=float, default=0.4, help="detection confidence (0.3 more sensitive, 0.5 stricter)")
parser.add_argument("--model", default="yolov8n.pt", help="yolov8n.pt = fast, yolov8s.pt = more accurate")
args = parser.parse_args()

source = int(args.source) if args.source.isdigit() else args.source
cap = cv2.VideoCapture(source)
if not cap.isOpened():
    raise SystemExit("Could not open the camera/video. Try --source 1 or check the file path.")

model = YOLO(args.model)          # first run downloads the weights (needs internet once)

history = deque(maxlen=8)         # last 8 checks
last_sent = None
last_sent_time = 0.0
frame_no = 0
count = 0
boxes = []


def send(persons):
    body = json.dumps({"persons": persons}).encode()
    req = urllib.request.Request(
        f"{args.api}/api/rooms/{args.room}/occupancy", data=body,
        headers={"Content-Type": "application/json"}, method="POST")
    urllib.request.urlopen(req, timeout=2).read()


print(f"Watching room {args.room} with {args.model}. Press q in the video window to quit.")
while True:
    ok, frame = cap.read()
    if not ok:
        if isinstance(source, str):          # video file ended: loop it
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        break
    frame_no += 1

    if frame_no % 3 == 0:                    # detect on every 3rd frame
        result = model.predict(frame, classes=[0], conf=args.conf, imgsz=640, verbose=False)[0]
        boxes = [tuple(map(int, b.xyxy[0].tolist())) for b in result.boxes]
        history.append(len(boxes))
        # say "empty" only if ALL recent checks saw nobody
        count = max(history)

    now = time.time()
    if len(history) >= 5 and (count != last_sent or now - last_sent_time > 3):
        try:
            send(count)
            last_sent, last_sent_time = count, now
        except Exception as e:
            print("Could not reach the API (is the server running?)", e)
            last_sent_time = now

    for (x1, y1, x2, y2) in boxes:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), 2)
    cv2.putText(frame, f"Room {args.room}: {count} person(s)", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
    cv2.imshow("CampusBuddy camera (YOLO)", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()