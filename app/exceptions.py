from fastapi import HTTPException, status


CameraAlreadyRunningException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Ошибка: Камера уже запущена",
)
CameraAlreadyStoppedException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Ошибка: Камера уже остановлена",
)
InvalidDateRangeException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Ошибка: параметр 'start' не может быть позже 'end'.",
)
