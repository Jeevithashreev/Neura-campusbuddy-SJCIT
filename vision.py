"""CampusBuddy Step 2: camera counts people and sends the number to the API.
Nothing is saved: frames are used in memory and thrown away."""
import argparse
import json
import time
import urllib.request
from collections import deque

import cv2

parser = argparse.ArgumentParser()
parser.add_argument("--room", type=int, default=2, help="room id this camera watches")
parser.add_argument("--source", default="0", help="0 for webcam, or a video file path")
parser.add_argument("--api", default="http://127.0.0.1:8000")
args = parser.parse_args()

source = int(args.source) if args.source.isdigit() else args.source
cap = cv2.VideoCapture(source)
if not cap.isOpened():
    raise SystemExit("Could not open the camera/video. Try --source 1 or check the file path.")

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

history = deque(maxlen=15)   # last 15 checks
last_sent = None
last_sent_time = 0.0
frame_no = 0
count = 0


def send(persons):
    body = json.dumps({"persons": persons}).encode()
    req = urllib.request.Request(
        f"{args.api}/api/rooms/{args.room}/occupancy", data=body,
        headers={"Content-Type": "application/json"}, method="POST")
    urllib.request.urlopen(req, timeout=2).read()


def count_people(frame):
    h, w = frame.shape[:2]
    scale = 640 / w
    small = cv2.resize(frame, (640, int(h * scale)))
    rects, weights = hog.detectMultiScale(small, winStride=(8, 8), padding=(8, 8), scale=1.05)
    if len(rects) == 0:
        return 0, []
    boxes = [list(map(int, r)) for r in rects]
    scores = [float(x) for x in weights]
    keep = cv2.dnn.NMSBoxes(boxes, scores, 0.4, 0.4)
    keep = [int(k) for k in (keep.flatten() if hasattr(keep, "flatten") else keep)]
    final = [boxes[i] for i in keep]
    return len(final), [(int(x / scale), int(y / scale), int(bw / scale), int(bh / scale)) for x, y, bw, bh in final]


print(f"Watching room {args.room}. Press q in the video window to quit.")
boxes = []
while True:
    ok, frame = cap.read()
    if not ok:
        if isinstance(source, str):          # video file ended: loop it
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        break
    frame_no += 1

    if frame_no % 3 == 0:                    # detect on every 3rd frame (saves CPU)
        n, boxes = count_people(frame)
        history.append(n)
        # Be careful about saying "empty": only if the last checks ALL saw nobody
        count = max(history)

    # send when the count changes, and every 3 seconds as a heartbeat
    now = time.time()
    if len(history) >= 5 and (count != last_sent or now - last_sent_time > 3):
        try:
            send(count)
            last_sent, last_sent_time = count, now
        except Exception as e:
            print("Could not reach the API (is the server running?)", e)
            last_sent_time = now

    for (x, y, w, h) in boxes:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 200, 0), 2)
    cv2.putText(frame, f"Room {args.room}: {count} person(s)", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
    cv2.imshow("CampusBuddy camera", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()