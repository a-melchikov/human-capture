import asyncio
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from app.services.detectors import detector


class State:
    def __init__(self) -> None:
        self.event_queue: asyncio.Queue[Any] = asyncio.Queue()
        self.detector_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()


app_state = State()


@asynccontextmanager
async def lifespan(app: FastAPI):
    detector.event_queue = app_state.event_queue  # type: ignore
    detector.loop = app_state.detector_loop  # type: ignore
    yield
