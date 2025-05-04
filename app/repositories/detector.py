from datetime import datetime

from sqlalchemy import select

from app.database.core import async_session_maker
from app.models.detector import Detection
from app.repositories.sqlalchemy_repository import SQLAlchemyRepository


class DetectionDAO(SQLAlchemyRepository[Detection]):
    model = Detection

    @classmethod
    async def get_detections_by_date(
        cls, start: datetime, end: datetime
    ) -> list[Detection]:
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .where(cls.model.timestamp >= start, cls.model.timestamp <= end)
                .order_by(cls.model.timestamp.desc())
            )
            result = await session.execute(query)
            return list(result.scalars().all())
