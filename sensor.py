"""Fake room sensor: sends a people count for one building to the server over the network."""
import json
import sys
import urllib.request

room = int(sys.argv[1])      # building number: 1 to 5
persons = int(sys.argv[2])   # 0 = empty, 1 or more = people inside

body = json.dumps({"persons": persons}).encode()
req = urllib.request.Request(
    f"http://127.0.0.1:8000/api/rooms/{room}/occupancy",
    data=body, headers={"Content-Type": "application/json"}, method="POST")
urllib.request.urlopen(req, timeout=2).read()
print(f"Sensor sent: room {room} has {persons} person(s)")