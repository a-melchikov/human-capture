import cv2
import mediapipe as mp
import time
import os

from config import load_config

settings = load_config()


def initialize_pose_detection():
    mp_pose = mp.solutions.pose
    return mp_pose.Pose()


def get_roi(frame: cv2.Mat) -> cv2.Mat:
    height, width = frame.shape[:2]

    if settings.x + settings.width > width or settings.y + settings.height > height:
        return None

    return frame[
        settings.x : settings.y + settings.height,
        settings.x : settings.x + settings.width,
    ]


def process_frame(pose, frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return pose.process(rgb)


def is_human_detected(results, min_visible_points, visibility_threshold):
    if not results.pose_landmarks:
        return False

    visible_points = [
        lmk
        for lmk in results.pose_landmarks.landmark
        if lmk.visibility > visibility_threshold
    ]
    return len(visible_points) > min_visible_points


def save_human_photo(frame):
    filename = f"{settings.save_path}/human_{int(time.time())}.jpg"
    cv2.imwrite(filename, frame)
    print(f"Человек обнаружен. Фото сохранено: {filename}")
    return filename


def draw_roi(frame: cv2.Mat) -> None:
    pt1 = (settings.x, settings.y)
    pt2 = (settings.x + settings.width, settings.y + settings.height)
    color = (0, 255, 0)
    cv2.rectangle(
        frame,
        pt1=pt1,
        pt2=pt2,
        color=color,
        thickness=2,
    )


def main():
    os.makedirs(settings.save_path, exist_ok=True)
    pose = initialize_pose_detection()
    cap = cv2.VideoCapture(0)
    photo_saved = False

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            roi = get_roi(frame)
            if roi is None:
                print("Error: ROI выходит за границы")
                break

            results = process_frame(pose, roi)

            if (
                is_human_detected(
                    results,
                    settings.min_visible_points,
                    settings.visibility_threshold,
                )
                and not photo_saved
            ):
                save_human_photo(frame)
                photo_saved = True

            draw_roi(frame)
            cv2.imshow("Human Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
