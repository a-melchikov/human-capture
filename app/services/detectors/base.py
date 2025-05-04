import asyncio
import logging
import threading
import time

import cv2

from app.core.config import Settings, settings
from app.services.detectors.camera_manager import CameraManager
from app.services.detectors.detection_saver import DetectionSaver
from app.services.detectors.face_detector import FaceDetector
from app.services.detectors.frame_processor import FrameProcessor

logger = logging.getLogger(__name__)


class HumanDetector:
    def __init__(self, settings: Settings, show_camera: bool = False):
        self.face_detector = FaceDetector()
        self.frame_processor = FrameProcessor(settings)
        self.detection_saver = DetectionSaver(settings)
        self.camera = CameraManager()

        self.settings = settings
        self.window_name = "Human Detection"
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        self.detection_start_time = None
        self.last_save_time = 0
        self.event_queue = None
        self.loop = None
        self.show_camera = show_camera

    def _run(self) -> None:
        try:
            if not self.camera.open():
                self.running = False
                return

            while self.running:
                frame = self.camera.read_frame()
                if frame is None:
                    continue

                roi = self.frame_processor.get_roi(frame)
                if roi is None:
                    logger.error("ROI выходит за границы кадра")
                    break

                results = self.face_detector.process(roi)

                if self.face_detector.is_human_detected(results):
                    current_time = time.time()

                    if self.detection_start_time is None:
                        self.detection_start_time = current_time
                    elif current_time - self.detection_start_time >= 5:
                        if current_time - self.last_save_time >= 5:
                            detection = results.detections[0]
                            x_rel, y_rel, w_rel, h_rel = (
                                self.face_detector.get_face_bounding_box(
                                    detection, roi.shape
                                )
                            )

                            x_abs: int = x_rel + self.settings.x
                            y_abs: int = y_rel + self.settings.y

                            image_path = self.detection_saver.save_human_image(
                                frame, x_abs, y_abs, w_rel, h_rel
                            )
                            if image_path:
                                asyncio.run_coroutine_threadsafe(
                                    self.detection_saver.save_to_database(image_path),
                                    self.loop,
                                )

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
                    cv2.imshow(self.window_name, frame)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        self.running = False

        except Exception as e:
            logger.error("Ошибка в потоке детектора: %s", repr(e))
        finally:
            with self.lock:
                self.camera.release()
                if self.show_camera:
                    cv2.destroyWindow(self.window_name)
                    cv2.waitKey(1)
                self.running = False
            logger.info("Камера и окна закрыты")

    def start(self):
        with self.lock:
            if not self.running:
                for _ in range(5):
                    if self.camera.is_camera_free():
                        break
                    time.sleep(0.5)
                else:
                    logger.error("Камера занята, невозможно запустить")
                    return

                self.running = True
                self.thread = threading.Thread(target=self._run)
                self.thread.start()
                logger.info("Камера успешно запущена")

    def stop(self):
        with self.lock:
            if self.running:
                self.running = False
                if self.thread and self.thread.is_alive():
                    self.thread.join(timeout=1.0)
                    if self.thread.is_alive():
                        logger.warning("Поток завис, принудительное завершение")
                        self.camera.release()
                self.thread = None
                logger.info("Камера остановлена")


detector = HumanDetector(
    settings=settings,
    show_camera=settings.show_camera,
)
