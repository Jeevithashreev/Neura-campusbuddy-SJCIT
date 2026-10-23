"""CampusBuddy extra features: events, registration, feedback, place reports.
Data is kept in memory and saved to data.json, so a restart does not lose it.
Demo level only: there are no passwords, and the admin routes are open."""
import json
import os
import threading
import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

DATA_FILE = os.getenv("CAMPUS_DATA_FILE", "data.json")
LOCK = threading.Lock()
router = APIRouter()

KINDS = ["Cut wire", "Water leak", "Water wastage", "Broken item", "Other"]


def _seed(now):
    return {
        "events": [
            {"id": 1, "title": "Coding workshop", "place": "IT Block", "start": now + 60,
             "duration_min": 3, "description": "Short live-coding session (demo event)."},
            {"id": 2, "title": "Guest lecture: AI in everyday life", "place": "Library",
             "start": now + 30 * 60, "duration_min": 60, "description": "Open to all departments."},
            {"id": 3, "title": "Tech quiz", "place": "Admin Block", "start": now - 3 * 3600,
             "duration_min": 60, "description": "Held earlier today."},
        ],
        "registrations": [], "feedback": [], "reports": [],
    }


def _load():
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        data = _seed(time.time())
        _save(data)
        return data


def _save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)


DATA = _load()


def _clean(text, limit=300):
    return (text or "").strip()[:limit]


def event_status(ev, now):
    end = ev["start"] + ev["duration_min"] * 60
    if now < ev["start"]:
        return "upcoming"
    return "live" if now < end else "ended"


def _event_view(ev, now):
    regs = [r for r in DATA["registrations"] if r["event_id"] == ev["id"]]
    fbs = [f for f in DATA["feedback"] if f["event_id"] == ev["id"]]
    avg = round(sum(f["rating"] for f in fbs) / len(fbs), 1) if fbs else None
    return {
        "id": ev["id"], "title": ev["title"], "place": ev["place"],
        "description": ev["description"], "duration_min": ev["duration_min"],
        "start_text": time.strftime("%H:%M", time.localtime(ev["start"])),
        "starts_in_min": round((ev["start"] - now) / 60, 1),
        "status": event_status(ev, now),
        "registered": len(regs), "feedback_count": len(fbs), "avg_rating": avg,
    }


class NewEvent(BaseModel):
    title: str
    place: str
    start_in_min: float = 5
    duration_min: int = 30
    description: str = ""


class Registration(BaseModel):
    name: str
    usn: str


class Feedback(BaseModel):
    rating: int
    comment: str = ""


class Report(BaseModel):
    place: str
    kind: str
    note: str = ""
    lat: float | None = None
    lng: float | None = None


def _find_event(event_id):
    for ev in DATA["events"]:
        if ev["id"] == event_id:
            return ev
    raise HTTPException(404, "unknown event")


@router.get("/api/events")
def list_events():
    now = time.time()
    order = {"live": 0, "upcoming": 1, "ended": 2}
    views = [_event_view(e, now) for e in DATA["events"]]
    return sorted(views, key=lambda v: (order[v["status"]], v["starts_in_min"]))


@router.post("/api/events")
def create_event(body: NewEvent):
    title, place = _clean(body.title, 100), _clean(body.place, 100)
    if not title or not place:
        raise HTTPException(400, "title and place are required")
    with LOCK:
        new_id = max([e["id"] for e in DATA["events"]] + [0]) + 1
        DATA["events"].append({
            "id": new_id, "title": title, "place": place,
            "start": time.time() + max(0, body.start_in_min) * 60,
            "duration_min": max(1, min(body.duration_min, 600)),
            "description": _clean(body.description)})
        _save(DATA)
    return {"ok": True, "id": new_id}


@router.post("/api/events/{event_id}/register")
def register(event_id: int, body: Registration):
    ev = _find_event(event_id)
    name, usn = _clean(body.name, 80), _clean(body.usn, 20).upper()
    if not name or not usn:
        raise HTTPException(400, "name and USN are required")
    if event_status(ev, time.time()) == "ended":
        raise HTTPException(400, "this event has ended")
    with LOCK:
        if any(r["event_id"] == event_id and r["usn"] == usn for r in DATA["registrations"]):
            raise HTTPException(400, "already registered")
        DATA["registrations"].append({"event_id": event_id, "name": name, "usn": usn, "ts": time.time()})
        _save(DATA)
    return {"ok": True}


@router.post("/api/events/{event_id}/feedback")
def give_feedback(event_id: int, body: Feedback):
    ev = _find_event(event_id)
    if event_status(ev, time.time()) != "ended":
        raise HTTPException(400, "feedback opens when the event ends")
    if not 1 <= body.rating <= 5:
        raise HTTPException(400, "rating must be 1 to 5")
    with LOCK:
        DATA["feedback"].append({"event_id": event_id, "rating": body.rating,
                                 "comment": _clean(body.comment), "ts": time.time()})
        _save(DATA)
    return {"ok": True}


@router.post("/api/reports")
def add_report(body: Report):
    if body.kind not in KINDS:
        raise HTTPException(400, "unknown problem type")
    place = _clean(body.place, 100)
    if not place:
        raise HTTPException(400, "place is required")
    with LOCK:
        new_id = max([r["id"] for r in DATA["reports"]] + [0]) + 1
        DATA["reports"].append({"id": new_id, "place": place, "kind": body.kind,
                                "note": _clean(body.note), "lat": body.lat, "lng": body.lng,
                                "status": "open", "ts": time.time()})
        _save(DATA)
    return {"ok": True, "id": new_id}


@router.post("/api/reports/{report_id}/resolve")
def resolve_report(report_id: int):
    with LOCK:
        for r in DATA["reports"]:
            if r["id"] == report_id:
                r["status"] = "resolved"
                _save(DATA)
                return {"ok": True}
    raise HTTPException(404, "unknown report")


@router.get("/api/kinds")
def report_kinds():
    return KINDS


@router.get("/api/admin/inbox")
def admin_inbox():
    now = time.time()
    events = []
    for ev in DATA["events"]:
        v = _event_view(ev, now)
        v["comments"] = [{"rating": f["rating"], "comment": f["comment"]}
                         for f in DATA["feedback"] if f["event_id"] == ev["id"]]
        v["people"] = [{"name": r["name"], "usn": r["usn"]}
                       for r in DATA["registrations"] if r["event_id"] == ev["id"]]
        events.append(v)
    reports = sorted(DATA["reports"], key=lambda r: (r["status"] != "open", -r["ts"]))
    return {"events": events, "reports": reports}