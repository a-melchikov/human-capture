from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()


@router.get(
    "/",
    summary="Главная страница",
    description="Возвращает основную страницу приложения",
    response_class=FileResponse,
    tags=["Главная"],
)
async def read_index() -> FileResponse:
    return FileResponse("static/index.html")
