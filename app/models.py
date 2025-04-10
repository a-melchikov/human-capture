import pytz

from datetime import datetime
from sqlalchemy import TIMESTAMP
from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column


class Detection(Base):
    __tablename__ = "detections"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(pytz.timezone("Europe/Samara")),
        index=True,
    )
    image_path: Mapped[str]
    x: Mapped[int]
    y: Mapped[int]
    width: Mapped[int]
    height: Mapped[int]
