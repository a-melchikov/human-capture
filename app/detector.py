import cv2
import mediapipe as mp
import time
import os
import threading

from app.config import load_config

settings = load_config()


class HumanDetector:
    def __init__(self):
        self.cap = None
        self.running = False
        self.thread = None
        self.photo_saved = False
        self.lock = threading.Lock()

    def initialize_pose_detection(self):
        mp_pose = mp.solutions.pose
        return mp_pose.Pose()

    def get_roi(self, frame: cv2.Mat) -> cv2.Mat | None:
        height, width = frame.shape[:2]

        if settings.x + settings.width > width or settings.y + settings.height > height:
            return None

        return frame[
            settings.y : settings.y + settings.height,
            settings.x : settings.x + settings.width,
        ]

    def process_frame(self, pose, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return pose.process(rgb)

    def is_human_detected(self, results, min_visible_points, visibility_threshold):
        if not results.pose_landmarks:
            return False

        visible_points = [
            lmk
            for lmk in results.pose_landmarks.landmark
            if lmk.visibility > visibility_threshold
        ]
        return len(visible_points) > min_visible_points

    def save_human_photo(self, frame):
        filename = f"{settings.save_path}/human_{int(time.time())}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Человек обнаружен. Фото сохранено: {filename}")
        return filename

    def draw_roi(self, frame: cv2.Mat) -> None:
        pt1 = (settings.x, settings.y)
        pt2 = (settings.x + settings.width, settings.y + settings.height)
        cv2.rectangle(frame, pt1=pt1, pt2=pt2, color=(0, 255, 0), thickness=2)

    def _run(self):
        os.makedirs(settings.save_path, exist_ok=True)
        pose = self.initialize_pose_detection()
        self.cap = cv2.VideoCapture(0)
        self.photo_saved = False

        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            roi = self.get_roi(frame)
            if roi is None:
                print("Error: ROI выходит за границы")
                break

            results = self.process_frame(pose, roi)

            if self.is_human_detected(
                results, settings.min_visible_points, settings.visibility_threshold
            ):
                if not self.photo_saved:
                    self.save_human_photo(frame)
                    self.photo_saved = True

            # self.draw_roi(frame)
            # cv2.imshow("Human Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        if self.cap:
            self.cap.release()
        # cv2.destroyAllWindows()
        self.running = False

    def start(self):
        with self.lock:
            if not self.running:
                self.running = True
                self.thread = threading.Thread(target=self._run)
                self.thread.start()
                print("Камера запущена.")

    def stop(self):
        with self.lock:
            if self.running:
                self.running = False
                if self.thread and self.thread.is_alive():
                    self.thread.join()
                print("Камера остановлена.")


detector = HumanDetector()
