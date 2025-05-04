import asyncio
import logging
import os
import threading
import time
from typing import Any, NamedTuple

import cv2
from mediapipe.python.solutions.face_detection import FaceDetection

from app.core.config import Settings, settings
from app.dao.detector import DetectionDAO

logger = logging.getLogger(__name__)


class FaceDetector:
    def __init__(self):
        self.detector = FaceDetection(
            model_selection=settings.face_model_selection,
            min_detection_confidence=settings.face_min_detection_confidence,
        )

    def process(self, frame: cv2.typing.MatLike) -> NamedTuple:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return self.detector.process(rgb)

    def is_human_detected(self, results) -> bool:
        return bool(results.detections)


class FrameProcessor:
    def __init__(self, settings: Settings):
        self.settings: Settings = settings

    def get_roi(self, frame: cv2.typing.MatLike) -> cv2.typing.MatLike | None:
        height, width = frame.shape[:2]

        if (
            self.settings.x + self.settings.width > width
            or self.settings.y + self.settings.height > height
        ):
            return None

        return frame[
            self.settings.y : self.settings.y + self.settings.height,
            self.settings.x : self.settings.x + self.settings.width,
        ]

    def draw_roi(self, frame: cv2.typing.MatLike):
        pt1 = (self.settings.x, self.settings.y)
        pt2 = (
            self.settings.x + self.settings.width,
            self.settings.y + self.settings.height,
        )
        cv2.rectangle(frame, pt1=pt1, pt2=pt2, color=(0, 255, 0), thickness=2)


class DetectionEventPublisher:
    def __init__(
        self, event_queue: asyncio.Queue[Any], loop: asyncio.AbstractEventLoop
    ) -> None:
        self.event_queue = event_queue
        self.loop = loop

    def publish(self, image_path: str):
        if self.event_queue and self.loop:
            event_data: dict[str, str | int] = {
                "image_path": image_path,
                "timestamp": int(time.time()),
            }
            self.loop.call_soon_threadsafe(self.event_queue.put_nowait, event_data)


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

    def save_human_image(self, frame: cv2.typing.MatLike) -> str | None:
        roi = frame[
            self.settings.y : self.settings.y + self.settings.height,
            self.settings.x : self.settings.x + self.settings.width,
        ]
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


class HumanDetector:
    def __init__(self, settings: Settings, show_camera: bool = False):
        self.face_detector = FaceDetector()
        self.frame_processor = FrameProcessor(settings)
        self.detection_saver = DetectionSaver(settings)

        self.cap = None
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        self.detection_start_time = None
        self.last_save_time = 0
        self.event_queue = None
        self.loop = None
        self.show_camera = show_camera

    def _run(self) -> None:
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Не удалось подключиться к камере")

        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            roi = self.frame_processor.get_roi(frame)
            if roi is None:
                logger.error("Ошибка, ROI выходит за границы")
                break

            results = self.face_detector.process(roi)

            if self.face_detector.is_human_detected(results):
                current_time = time.time()

                if self.detection_start_time is None:
                    self.detection_start_time = current_time
                elif current_time - self.detection_start_time >= 5:
                    if current_time - self.last_save_time >= 5:
                        image_path: str | None = self.detection_saver.save_human_image(
                            frame
                        )

                        if image_path:
                            asyncio.run_coroutine_threadsafe(
                                self.detection_saver.save_to_database(image_path),
                                self.loop,
                            )

                        if self.event_queue and self.loop:
                            event_data: dict[str, str | int] = {
                                "image_path": image_path,
                                "timestamp": int(time.time()),
                            }
                            self.loop.call_soon_threadsafe(
                                self.event_queue.put_nowait, event_data
                            )

                        self.last_save_time = current_time
                        self.detection_start_time = None
            else:
                self.detection_start_time = None

            if self.show_camera:
                self.frame_processor.draw_roi(frame)
                cv2.imshow("Human Detection", frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        if self.cap.isOpened():
            self.cap.release()
            self.cap = None

        if self.show_camera:
            cv2.destroyAllWindows()
            cv2.waitKey(100)

        self.running = False

    def start(self):
        with self.lock:
            if not self.running:
                self.running = True
                self.thread = threading.Thread(target=self._run)
                self.thread.start()
                logger.info("Камера запущена.")

    def stop(self):
        with self.lock:
            if self.running:
                self.running = False
                if self.thread and self.thread.is_alive():
                    self.thread.join()
                logger.info("Камера остановлена.")


detector = HumanDetector(
    settings=settings,
    show_camera=settings.show_camera,
)
