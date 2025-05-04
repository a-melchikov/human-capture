import json

from pydantic import BaseModel, Field


class Settings(BaseModel):
    x: int = Field(100, ge=0, description="X-координата верхнего левого угла")
    y: int = Field(100, ge=0, description="Y-координата верхнего левого угла")
    width: int = Field(400, gt=0, description="Ширина области")
    height: int = Field(300, gt=0, description="Высота области")
    face_model_selection: int = Field(
        0, ge=0, le=1, description="Модель: 0 — ближняя, 1 — дальняя"
    )
    face_min_detection_confidence: float = Field(
        0.5,
        ge=0.0,
        le=1.0,
        description="Минимальное значение confidence для фиксации лица",
    )
    save_path: str = Field("saved_photos", description="Путь для сохранения фото")
    show_camera: bool = Field(
        False, description="Включение/выключение 'debug' окна opencv камеры"
    )


def load_config(config_path: str = "settings.json") -> Settings:
    try:
        with open(config_path) as f:
            raw_config = json.load(f)
            return Settings.model_validate(raw_config)
    except FileNotFoundError:
        default_config = Settings()  # type: ignore
        with open(config_path, "w") as f:
            json.dump(default_config.model_dump(), f, indent=4)
        return default_config


settings = load_config()


if __name__ == "__main__":
    settings = load_config()
    print(settings)
