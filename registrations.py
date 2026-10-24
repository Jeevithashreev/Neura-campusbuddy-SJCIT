import json
import os
import re
import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()
FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registrations.json")
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Signup(BaseModel):
    event: str
    name: str = ""
    email: str


def _load():
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save(data):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


@router.get("/api/signups")
def list_signups():
    return _load()


@router.post("/api/signups")
def add_signup(s: Signup):
    email = s.email.strip().lower()
    if not EMAIL.match(email):
        raise HTTPException(status_code=400, detail="Please enter a valid email address")
    data = _load()
    if any(d["event"] == s.event and d["email"] == email for d in data):
        raise HTTPException(status_code=400, detail="This email is already registered for this event")
    data.append({"event": s.event, "name": s.name.strip(), "email": email, "ts": time.time()})
    _save(data)
    return {"ok": True, "count": len([d for d in data if d["event"] == s.event])}