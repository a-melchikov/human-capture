from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
import asyncio
import json
from app.dao import DetectionDAO
from app.detector import detector
from app.config import settings
from app.schemas import DetectionOut
from app.database import session_maker

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


@app.get(
    "/humans",
    response_model=list[DetectionOut],
    summary="Получить фотографии людей за определённый период",
)
def get_detections_by_date(
    start: datetime = Query(
        default_factory=lambda: datetime.now() - timedelta(hours=1),
        description="Начало временного диапазона (по умолчанию: 1 час назад)",
        example="2025-04-09T10:00:00",
    ),
    end: datetime = Query(
        default_factory=datetime.now,
        description="Конец временного диапазона (по умолчанию: текущее время)",
        example="2025-04-09T15:00:00",
    ),
):
    if start > end:
        raise HTTPException(
            status_code=400, detail="Ошибка: параметр 'start' не может быть позже 'end'"
        )

    with session_maker() as session:
        dao = DetectionDAO(session)
        detections = dao.get_detections_by_date(start, end)

        return [
            DetectionOut(
                id=d.id,
                timestamp=d.timestamp,
                image_url=f"localhost:5000/saved_photos/{d.image_path.split('/')[-1]}",
            )
            for d in detections
        ]


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
