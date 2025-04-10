from fastapi import APIRouter, Query
from datetime import datetime, timedelta

import pytz
from app.database import session_maker
from app.dao import DetectionDAO
from app.schemas import DetectionOut
from app.exceptions import InvalidDateRangeException

router = APIRouter(tags=["Фотографии людей"])


@router.get(
    "/humans",
    response_model=list[DetectionOut],
    summary="Получить фотографии людей за определённый период",
    description="Возвращает список фотографий людей, найденных в определённом временном промежутке",
)
def get_detections_by_date(
    start: datetime = Query(
        default_factory=lambda: (
            datetime.now(pytz.timezone("Europe/Samara")) - timedelta(hours=1)
        ).replace(microsecond=0),
        description="Начало временного диапазона. По умолчанию: 1 час назад",
        example="2025-04-09T10:00:00",
    ),
    end: datetime = Query(
        default_factory=lambda: datetime.now(pytz.timezone("Europe/Samara")).replace(
            microsecond=0
        ),
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
