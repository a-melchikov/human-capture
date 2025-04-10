from pydantic import BaseModel, ConfigDict
from datetime import datetime


class DetectionOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")},
    )

    id: int
    timestamp: datetime
    image_url: str
