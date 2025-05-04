import asyncio
import logging
import os
import time
from typing import Any

import cv2

from app.core.config import Settings
from app.repositories.detector import DetectionDAO

logger = logging.getLogger(__name__)


class DetectionSaver:
    def __init__(
        self,
        settings: Settings,
        event_queue: asyncio.Queue[Any] | None = None,
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        self.settings = settings
        self.event_queue = event_queue
        self.loop = loop
        os.makedirs(settings.save_path, exist_ok=True)

    def save_human_image(
        self, frame: cv2.typing.MatLike, x: int, y: int, w: int, h: int
    ) -> str | None:
        h_img, w_img = frame.shape[:2]
        x = max(0, x)
        y = max(0, y)
        w = min(w, w_img - x)
        h = min(h, h_img - y)

        roi = frame[y : y + h, x : x + w]
        if roi.size == 0:
            return None

        path = f"{self.settings.save_path}/human_{int(time.time())}.jpg"
        success = cv2.imwrite(path, roi)

        if not success:
            logger.error("Ошибка при сохранении изображения в: %s", path)
            return None

        logger.info("Человек обнаружен. Фото сохранено: %s", path)
        return path

    async def save_to_database(self, image_path: str):
        await DetectionDAO.add(
            image_path=image_path,
            x=self.settings.x,
            y=self.settings.y,
            width=self.settings.width,
            height=self.settings.height,
        )
