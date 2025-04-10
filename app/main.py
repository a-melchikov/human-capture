from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.lifespan import lifespan
from app.routers import camera, photos, events, static
from app.config import settings

app = FastAPI(
    title="CameraAPI",
    description="Приложение для работы с камерой для обнаружения людей.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/saved_photos", StaticFiles(directory=settings.save_path), name="photos")

app.include_router(static.router)
app.include_router(camera.router)
app.include_router(photos.router)
app.include_router(events.router)
