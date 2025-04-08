from datetime import datetime

from sqlalchemy import func
from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column


class Detection(Base):
    __tablename__ = "detections"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(default=func.now())
    image_path: Mapped[str]
    x: Mapped[int]
    y: Mapped[int]
    width: Mapped[int]
    height: Mapped[int]
