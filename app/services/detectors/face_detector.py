from typing import NamedTuple

import cv2
from mediapipe.python.solutions.face_detection import FaceDetection

from app.core.config import settings


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

    def get_face_bounding_box(
        self, detection, frame_shape
    ) -> tuple[int, int, int, int]:
        relative_bbox = detection.location_data.relative_bounding_box
        h, w, _ = frame_shape
        x_min = int(relative_bbox.xmin * w)
        y_min = int(relative_bbox.ymin * h)
        box_width = int(relative_bbox.width * w)
        box_height = int(relative_bbox.height * h)
        return x_min, y_min, box_width, box_height
