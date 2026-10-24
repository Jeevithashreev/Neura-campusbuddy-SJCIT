import asyncio
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from copilot import ask as ask_copilot
from engine import Engine

engine = Engine()


async def ticker():
    while True:
        engine.tick(time.time())
        await asyncio.sleep(1)


@asynccontextmanager
async def lifespan(app):
    task = asyncio.create_task(ticker())
    yield
    task.cancel()


app = FastAPI(title="CampusBuddy: SJCIT", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


class Occupancy(BaseModel):
    persons: int


class Lights(BaseModel):
    on: bool


class Question(BaseModel):
    question: str


@app.get("/")
def home():
    return FileResponse("static/home.html")


@app.get("/api/state")
def get_state():
    return engine.state(time.time())


@app.post("/api/rooms/{room_id}/occupancy")
def set_occupancy(room_id: int, body: Occupancy):
    try:
        engine.set_persons(room_id, body.persons, time.time())
    except ValueError:
        raise HTTPException(404, "unknown room")
    return engine.state(time.time())


@app.post("/api/rooms/{room_id}/lights")
def set_lights(room_id: int, body: Lights):
    try:
        engine.set_lights(room_id, body.on, time.time())
    except ValueError:
        raise HTTPException(404, "unknown room")
    return engine.state(time.time())


@app.post("/api/reset")
def reset():
    engine.reset(time.time())
    return engine.state(time.time())


def fallback_answer(state):
    """Plain answer from live data, used when Gemini is not available."""
    rooms = state["rooms"]
    best = max(rooms, key=lambda r: r["saved_kwh"])
    off = [r["name"] for r in rooms if r["status"] == "switched_off"]
    waiting = [r["name"] for r in rooms if r["status"] in ("warning", "empty_lights_on")]
    people = sum(r["persons"] for r in rooms)
    parts = [f"Estimated savings so far: {state['saved_kwh']} kWh (Rs {state['saved_rupees']})."]
    if best["saved_kwh"] > 0:
        parts.append(f"{best['name']} has saved the most ({best['saved_kwh']} kWh).")
    if off:
        parts.append("Switched off now: " + ", ".join(off) + ".")
    if waiting:
        parts.append("Empty with lights still on: " + ", ".join(waiting) + ".")
    parts.append(f"{people} people are on campus right now.")
    return " ".join(parts)


AI_FAILURES = ("The copilot has no API key", "Gemini returned an error", "Could not reach Gemini")


@app.post("/api/copilot")
def copilot(body: Question):
    state = engine.state(time.time())
    answer = ask_copilot(body.question, state)
    if answer.startswith(AI_FAILURES):
        return {"answer": fallback_answer(state), "source": "backup (AI offline)"}
    return {"answer": answer, "source": "Gemini"}


import features
app.include_router(features.router)

from registrations import router as signups_router
app.include_router(signups_router)
