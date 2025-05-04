from datetime import datetime

import pytz
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Detection(Base):
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
