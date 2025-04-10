from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(tags=["Главная"])


@router.get(
    "/",
    summary="Главная страница",
    description="Возвращает основную страницу приложения",
    response_class=FileResponse,
)
async def read_index() -> FileResponse:
    return FileResponse("static/index.html")
