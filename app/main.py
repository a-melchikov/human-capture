from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
import asyncio
import json

from app.dao import DetectionDAO
from app.detector import detector
from app.config import settings
from app.exceptions import (
    CameraAlreadyRunningException,
    CameraAlreadyStoppedException,
    InvalidDateRangeException,
)
from app.schemas import DetectionOut
from app.database import session_maker


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


app = FastAPI(
    title="CameraAPI",
    description="Приложение для работы с камерой для обнаружения людей.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/saved_photos", StaticFiles(directory=settings.save_path), name="photos")


@app.get(
    "/",
    summary="Главная страница",
    description="Возвращает основную страницу приложения",
    response_class=FileResponse,
    tags=["Главная"],
)
async def read_index() -> FileResponse:
    return FileResponse("static/index.html")


@app.post(
    "/start",
    summary="Запуск камеры",
    description="Запускает камеру для определения людей в кадре. Если уже запущена возвращается ошибка",
    tags=["Управление камерой"],
)
def start_camera() -> dict[str, str] | None:
    if detector.running:
        raise CameraAlreadyRunningException
    detector.start()
    return {"status": "Камера запущена"}


@app.post(
    "/stop",
    summary="Остановка камеры",
    description="Останавливает камеру. Если уже остановлена возвращается ошибка",
    tags=["Управление камерой"],
)
def stop_camera() -> dict[str, str] | None:
    if not detector.running:
        raise CameraAlreadyStoppedException
    detector.stop()
    return {"status": "Камера остановлена"}


@app.get(
    "/humans",
    response_model=list[DetectionOut],
    summary="Получить фотографии людей за определённый период",
    description="Возвращает список фотографий людей, найденных в определённом временном промежутке",
    tags=["Фотографии людей"],
)
def get_detections_by_date(
    start: datetime = Query(
        default_factory=lambda: datetime.now() - timedelta(hours=1),
        description="Начало временного диапазона. По умолчанию: 1 час назад",
        example="2025-04-09T10:00:00",
    ),
    end: datetime = Query(
        default_factory=datetime.now,
        description="Конец временного диапазона. По умолчанию: текущее время",
        example="2025-04-09T15:00:00",
    ),
) -> list[DetectionOut] | None:
    if start > end:
        raise InvalidDateRangeException

    with session_maker() as session:
        dao = DetectionDAO(session)
        detections = dao.get_detections_by_date(start, end)

        return [
            DetectionOut(
                id=d.id,
                timestamp=d.timestamp,
                image_url=f"http://localhost:5000/saved_photos/{d.image_path.split('/')[-1]}",
            )
            for d in detections
        ]


async def event_generator():
    while True:
        event_data = await app_state.event_queue.get()
        yield f"data: {json.dumps(event_data)}\n\n"


@app.get(
    "/events",
    summary="Server-Sent Events",
    description="Позволяет получать события о новых добавленных фотографиях через SSE (Server-Sent Events)",
    response_class=StreamingResponse,
    tags=["SSE"],
)
async def events() -> StreamingResponse:
    return StreamingResponse(event_generator(), media_type="text/event-stream")
