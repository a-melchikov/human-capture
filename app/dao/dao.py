from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.detector import Detection


class DetectionDAO:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_detection(
        self, image_path: str, x: int, y: int, width: int, height: int
    ) -> Detection:
        detection = Detection(
            image_path=image_path, x=x, y=y, width=width, height=height
        )
        self.session.add(detection)
        await self.session.commit()
        await self.session.refresh(detection)
        return detection

    async def get_all_detections(self) -> list[Detection]:
        query = select(Detection)
        result = await self.session.execute(select(Detection))
        return result.scalars().all()

    async def get_detection_by_id(self, detection_id: int) -> Detection | None:
        result = await self.session.execute(
            select(Detection).where(Detection.id == detection_id)
        )
        return result.scalars().first()

    async def delete_detection(self, detection_id: int) -> bool:
        detection = await self.get_detection_by_id(detection_id)
        if detection:
            await self.session.delete(detection)
            await self.session.commit()
            return True
        return False

    async def get_detections_by_date(
        self, start: datetime, end: datetime
    ) -> list[Detection]:
        stmt = (
            select(Detection)
            .where(Detection.timestamp >= start, Detection.timestamp <= end)
            .order_by(Detection.timestamp.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
