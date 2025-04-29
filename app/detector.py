import logging
import os
import threading
import time

import cv2
import mediapipe as mp

from app.config import settings
from app.dao import DetectionDAO
from app.database import session_maker

logger = logging.getLogger(__name__)


class PoseDetector:
    def __init__(self):
        self.pose = mp.solutions.pose.Pose()
        self.min_visible_points = settings.min_visible_points
        self.visibility_threshold = settings.visibility_threshold

    def process(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return self.pose.process(rgb)

    def is_human_detected(self, results):
        if not results.pose_landmarks:
            return False

        visible_points = [
            lmk
            for lmk in results.pose_landmarks.landmark
            if lmk.visibility > self.visibility_threshold
        ]
        return len(visible_points) > self.min_visible_points


class FrameProcessor:
    def __init__(self, settings):
        self.settings = settings

    def get_roi(self, frame: cv2.Mat) -> cv2.Mat | None:
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

    def draw_roi(self, frame):
        pt1 = (self.settings.x, self.settings.y)
        pt2 = (
            self.settings.x + self.settings.width,
            self.settings.y + self.settings.height,
        )
        cv2.rectangle(frame, pt1=pt1, pt2=pt2, color=(0, 255, 0), thickness=2)


class DetectionEventPublisher:
    def __init__(self, event_queue, loop):
        self.event_queue = event_queue
        self.loop = loop

    def publish(self, image_path: str):
        if self.event_queue and self.loop:
            event_data = {
                "image_path": image_path,
                "timestamp": int(time.time()),
            }
            self.loop.call_soon_threadsafe(self.event_queue.put_nowait, event_data)


class DetectionSaver:
    def __init__(self, settings, event_queue=None, loop=None):
        self.settings = settings
        self.event_queue = event_queue
        self.loop = loop
        os.makedirs(settings.save_path, exist_ok=True)

    def save_human_image(self, frame):
        roi = frame[
            self.settings.y : self.settings.y + self.settings.height,
            self.settings.x : self.settings.x + self.settings.width,
        ]
        if roi is None:
            return None
        path = f"{self.settings.save_path}/human_{int(time.time())}.jpg"
        cv2.imwrite(path, roi)
        logger.info("Человек обнаружен. Фото сохранено: %s", path)
        return path

    def save_to_database(self, image_path):
        with session_maker() as session:
            try:
                detection_dao = DetectionDAO(session)
                detection_dao.add_detection(
                    image_path=image_path,
                    x=self.settings.x,
                    y=self.settings.y,
                    width=self.settings.width,
                    height=self.settings.height,
                )
            except Exception as e:
                session.rollback()
                logger.error("Ошибка при сохранении в базу данных: %s", e)
                raise
            else:
                session.commit()


class HumanDetector:
    def __init__(self, settings, show_camera: bool = False):
        self.pose_detector = PoseDetector()
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

    def _run(self):
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

            results = self.pose_detector.process(roi)

            if self.pose_detector.is_human_detected(results):
                current_time = time.time()

                if self.detection_start_time is None:
                    self.detection_start_time = current_time
                elif current_time - self.detection_start_time >= 5:
                    if current_time - self.last_save_time >= 5:
                        image_path = self.detection_saver.save_human_image(frame)
                        self.detection_saver.save_to_database(image_path)

                        if self.event_queue and self.loop:
                            event_data = {
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

        if self.show_camera:
            cv2.destroyAllWindows()

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
