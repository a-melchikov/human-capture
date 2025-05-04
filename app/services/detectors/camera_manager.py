import logging

import cv2

logger = logging.getLogger(__name__)


class CameraManager:
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.cap = None

    def open(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            logger.error("Не удалось открыть камеру")
            return False
        return True

    def read_frame(self):
        if self.cap:
            ret, frame = self.cap.read()
            if not ret:
                logger.error("Ошибка при чтении кадра")
                return None
            return frame
        return None

    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None

    def is_camera_free(self) -> bool:
        test_cap = cv2.VideoCapture(self.camera_index)
        if test_cap.isOpened():
            test_cap.release()
            return True
        return False
