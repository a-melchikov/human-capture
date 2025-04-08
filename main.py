import cv2
import mediapipe as mp
import time
import os

DIRECTORY = "saved_photos"


def initialize_pose_detection():
    mp_pose = mp.solutions.pose
    return mp_pose.Pose()


def process_frame(pose, frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return pose.process(rgb)


def is_human_detected(results, min_visible_points=20, visibility_threshold=0.5):
    if not results.pose_landmarks:
        return False

    visible_points = [
        lmk
        for lmk in results.pose_landmarks.landmark
        if lmk.visibility > visibility_threshold
    ]
    return len(visible_points) > min_visible_points


def save_human_photo(frame):
    filename = f"{DIRECTORY}/human_{int(time.time())}.jpg"
    cv2.imwrite(filename, frame)
    print(f"Человек обнаружен. Фото сохранено: {filename}")
    return filename


def main():
    os.makedirs(DIRECTORY, exist_ok=True)
    pose = initialize_pose_detection()
    cap = cv2.VideoCapture(0)
    photo_saved = False

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = process_frame(pose, frame)

            if is_human_detected(results) and not photo_saved:
                save_human_photo(frame)
                photo_saved = True

            cv2.imshow("Human Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
