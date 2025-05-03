from fastapi import APIRouter

from app.detector import detector
from app.exceptions import CameraAlreadyRunningException, CameraAlreadyStoppedException

router = APIRouter(tags=["Управление камерой"])


@router.post(
    "/start",
    summary="Запуск камеры",
    description="Запускает камеру для определения людей в кадре. Если уже запущена возвращается ошибка",
)
def start_camera() -> dict[str, str] | None:
    if detector.running:
        raise CameraAlreadyRunningException
    detector.start()
    return {"status": "Камера запущена"}


@router.post(
    "/stop",
    summary="Остановка камеры",
    description="Останавливает камеру. Если уже остановлена возвращается ошибка",
    tags=["Управление камерой"],
)
def stop_camera() -> dict[str, str] | None:
    if not detector.running:
        raise CameraAlreadyStoppedException
    detector.stop()
    return {"status": "Камера остановлена"}
