"""CampusBuddy engine: the rules that decide warn / switch off / save."""
import os
import time

WARN_AFTER = float(os.getenv("WARN_AFTER", 10))   # seconds empty before a warning
OFF_AFTER = float(os.getenv("OFF_AFTER", 20))     # seconds empty before auto switch-off
TIME_SCALE = float(os.getenv("TIME_SCALE", 60))   # 1 real second counts as 60 seconds
TARIFF = float(os.getenv("TARIFF", 8))            # rupees per kWh (assumption)
ROOM_POWER_W = float(os.getenv("ROOM_POWER_W", 420))  # 6 tube lights + 4 fans (assumption)


class Room:
    def __init__(self, room_id, name, persons, now):
        self.id = room_id
        self.name = name
        self.power_w = ROOM_POWER_W
        self.persons = persons
        self.lights_on = True
        self.auto_off = False          # True when the SYSTEM switched it off
        self.warned = False
        self.empty_since = None if persons > 0 else now


class Engine:
    def __init__(self, now=None):
        self.reset(now if now is not None else time.time())

    def reset(self, now):
        self.last_tick = now
        self.saved_kwh = 0.0
        self.events = []
        names = ["Room 101", "Room 102", "Room 103", "Room 104", "Room 105"]
        people = [2, 0, 3, 0, 1]
        self.rooms = [Room(i + 1, n, p, now) for i, (n, p) in enumerate(zip(names, people))]
        self.log("Demo started", now)

    def log(self, msg, now):
        self.events.insert(0, {"time": time.strftime("%H:%M:%S", time.localtime(now)), "msg": msg})
        del self.events[30:]

    def room(self, room_id):
        for r in self.rooms:
            if r.id == room_id:
                return r
        raise ValueError("unknown room")

    # inputs (camera or sensors will call these)
    def set_persons(self, room_id, persons, now):
        r = self.room(room_id)
        persons = max(0, int(persons))
        if persons > 0:
            if r.persons == 0:
                self.log(f"{r.name}: person entered", now)
            r.persons = persons
            r.empty_since = None
            r.warned = False
            if not r.lights_on:
                r.lights_on = True
                self.log(f"{r.name}: lights back on", now)
            r.auto_off = False
        else:
            if r.persons > 0 or r.empty_since is None:
                r.empty_since = now
                r.warned = False
                self.log(f"{r.name}: now empty", now)
            r.persons = 0

    def set_lights(self, room_id, on, now):
        """Manual override by staff."""
        r = self.room(room_id)
        r.lights_on = bool(on)
        r.auto_off = False
        r.warned = False
        if on and r.persons == 0:
            r.empty_since = now        # restart the countdown
        self.log(f"{r.name}: lights {'ON' if on else 'OFF'} (manual)", now)

    # the rules
    def tick(self, now):
        dt = max(0.0, now - self.last_tick)
        self.last_tick = now
        for r in self.rooms:
            if r.persons == 0 and r.lights_on and r.empty_since is not None:
                empty_for = now - r.empty_since
                if empty_for >= OFF_AFTER:
                    r.lights_on = False
                    r.auto_off = True
                    self.log(f"{r.name}: auto switch-off", now)
                elif empty_for >= WARN_AFTER and not r.warned:
                    r.warned = True
                    self.log(f"{r.name}: warning, empty with lights on", now)
            if r.persons == 0 and not r.lights_on and r.auto_off:
                self.saved_kwh += (r.power_w / 1000.0) * (dt * TIME_SCALE / 3600.0)

    def status(self, r, now):
        if r.persons > 0:
            return "occupied"
        if r.lights_on:
            empty_for = now - r.empty_since if r.empty_since else 0
            return "warning" if empty_for >= WARN_AFTER else "empty_lights_on"
        return "switched_off"

    def state(self, now):
        rooms = []
        for r in self.rooms:
            empty_for = round(now - r.empty_since, 1) if r.empty_since else 0
            rooms.append({
                "id": r.id, "name": r.name, "persons": r.persons,
                "lights_on": r.lights_on, "status": self.status(r, now),
                "empty_for": empty_for,
            })
        return {
            "rooms": rooms,
            "saved_kwh": round(self.saved_kwh, 3),
            "saved_rupees": round(self.saved_kwh * TARIFF, 2),
            "events": self.events[:10],
            "config": {"warn_after": WARN_AFTER, "off_after": OFF_AFTER,
                       "time_scale": TIME_SCALE, "tariff": TARIFF},
        }