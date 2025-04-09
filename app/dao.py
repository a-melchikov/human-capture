from sqlalchemy.orm import Session
from app.models import Detection


class DetectionDAO:
    def __init__(self, session: Session):
        self.session = session

    def add_detection(
        self, image_path: str, x: int, y: int, width: int, height: int
    ) -> Detection:
        detection = Detection(
            image_path=image_path, x=x, y=y, width=width, height=height
        )
        self.session.add(detection)
        self.session.commit()
        self.session.refresh(detection)
        return detection

    def get_all_detections(self) -> list[Detection]:
        return self.session.query(Detection).all()

    def get_detection_by_id(self, detection_id: int) -> Detection:
        return (
            self.session.query(Detection).filter(Detection.id == detection_id).first()
        )

    def delete_detection(self, detection_id: int) -> bool:
        detection = self.get_detection_by_id(detection_id)
        if detection:
            self.session.delete(detection)
            self.session.commit()
            return True
        return False
