from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    JSON
)

from sqlalchemy.orm import declarative_base


Base = declarative_base()


class DetectionEvent(Base):

    __tablename__ = "detection_events"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    video_name = Column(
        String(255)
    )

    source_id = Column(
        String(100)
    )

    object_id = Column(
        Integer
    )

    object_class = Column(
        String(100)
    )

    confidence = Column(
        Float
    )

    timestamp = Column(
        DateTime
    )

    frame_number = Column(
        Integer
    )

    bbox = Column(
        JSON
    )

    # Activity information
    activity = Column(
        String(50)
    )

    activity_start_time = Column(
        DateTime
    )

    activity_end_time = Column(
        DateTime
    )

    activity_duration_seconds = Column(
        Float
    )

    json_data = Column(
        JSON
    )

    created_on = Column(
        DateTime,
        default=datetime.utcnow
    )