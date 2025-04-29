import json

from pydantic import BaseModel, Field


class Settings(BaseModel):
    x: int = Field(100, ge=0, description="X-координата верхнего левого угла")
    y: int = Field(100, ge=0, description="Y-координата верхнего левого угла")
    width: int = Field(400, gt=0, description="Ширина области")
    height: int = Field(300, gt=0, description="Высота области")
    min_visible_points: int = Field(
        20, ge=1, le=33, description="Минимальное кол-во видимых точек"
    )
    visibility_threshold: float = Field(
        0.5, gt=0, le=1, description="Порог видимости точек"
    )
    save_path: str = Field("saved_photos", description="Путь для сохранения фото")


def load_config(config_path: str = "settings.json") -> Settings:
    try:
        with open(config_path) as f:
            raw_config = json.load(f)
            return Settings.model_validate(raw_config)
    except FileNotFoundError:
        default_config = Settings()
        with open(config_path, "w") as f:
            json.dump(default_config.camera.dict(), f, indent=4)
        return default_config


settings = load_config()


if __name__ == "__main__":
    settings = load_config()
    print(settings)
