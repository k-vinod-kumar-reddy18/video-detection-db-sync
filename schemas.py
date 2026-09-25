from datetime import datetime
from pydantic import BaseModel


class DetectionCreate(BaseModel):

    video_name: str

    source_id: str | None = None

    object_id: int | None = None

    object_class: str

    confidence: float

    timestamp: datetime

    frame_number: int

    bbox: list[float]

    activity: str | None = None

    activity_start_time: datetime | None = None

    activity_end_time: datetime | None = None

    activity_duration_seconds: float | None = None

    json_data: dict | None = None