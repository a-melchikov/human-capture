from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
import asyncio
import json
from app.detector import detector
from app.config import settings

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/saved_photos", StaticFiles(directory=settings.save_path), name="photos")


@app.get("/")
async def read_index():
    return FileResponse("static/index.html")


@app.post("/start")
def start_camera():
    if detector.running:
        return {"status": "Камера уже запущена"}
    detector.start()
    return {"status": "Камера запущена"}


@app.post("/stop")
def stop_camera():
    if not detector.running:
        return {"status": "Камера уже остановлена"}
    detector.stop()
    return {"status": "Камера остановлена"}


async def event_generator():
    while True:
        event_data = await event_queue.get()
        yield f"data: {json.dumps(event_data)}\n\n"


@app.get("/events")
async def events():
    return StreamingResponse(event_generator(), media_type="text/event-stream")


event_queue = None


@app.on_event("startup")
async def startup_event():
    global event_queue
    event_queue = asyncio.Queue()
    detector.event_queue = event_queue
    detector.loop = asyncio.get_event_loop()
