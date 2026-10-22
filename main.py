import asyncio
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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


@app.get("/")
def home():
    return FileResponse("static/index.html")


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