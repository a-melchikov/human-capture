import cv2

from app.core.config import Settings


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
