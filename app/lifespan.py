from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncio
from app.detector import detector


class State:
    def __init__(self):
        self.event_queue = asyncio.Queue()
        self.detector_loop = asyncio.get_event_loop()


app_state = State()


@asynccontextmanager
async def lifespan(app: FastAPI):
    detector.event_queue = app_state.event_queue
    detector.loop = app_state.detector_loop
    yield
