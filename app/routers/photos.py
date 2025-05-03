from datetime import datetime, timedelta

import pytz
from fastapi import APIRouter, Query

from app.dao.detector import DetectionDAO
from app.exceptions import InvalidDateRangeException
from app.schemas import DetectionOut

router = APIRouter(tags=["Фотографии людей"])


@router.get(
    "/humans",
    response_model=list[DetectionOut],
    summary="Получить фотографии людей за определённый период",
    description="Возвращает список фотографий людей, найденных в определённом временном промежутке",
)
async def get_detections_by_date(
    start: datetime = Query(  # noqa: B008
        default_factory=lambda: (
            datetime.now(pytz.timezone("Europe/Samara")) - timedelta(hours=1)
        ).replace(microsecond=0),
        description="Начало временного диапазона. По умолчанию: 1 час назад",
        example="2025-04-09T10:00:00",
    ),
    end: datetime = Query(  # noqa: B008
        default_factory=lambda: datetime.now(pytz.timezone("Europe/Samara")).replace(
            microsecond=0
        ),
        description="Конец временного диапазона. По умолчанию: текущее время",
        example="2025-04-09T15:00:00",
    ),
) -> list[DetectionOut] | None:
    if start > end:
        raise InvalidDateRangeException

    detections = await DetectionDAO.get_detections_by_date(start, end)

    return [
        DetectionOut(
            id=d.id,
            timestamp=d.timestamp,
            image_url=f"http://localhost:5000/saved_photos/{d.image_path.split('/')[-1]}",
        )
        for d in detections
    ]


@router.get(
    "/humans/all",
    response_model=list[DetectionOut],
    summary="Получить все фотографии",
    description="Возвращает список всех фотографий людей",
)
async def get_all_detections() -> list[DetectionOut]:
    detections = await DetectionDAO.find_all()

    return [
        DetectionOut(
            id=d.id,
            timestamp=d.timestamp,
            image_url=f"http://localhost:5000/saved_photos/{d.image_path.split('/')[-1]}",
        )
        for d in detections
    ]
