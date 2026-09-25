from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from postgres_database import get_db
from models import DetectionEvent
from schemas import DetectionCreate


app = FastAPI(
    title="Video Detection API",
    description="YOLO + FastAPI + PostgreSQL",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Video Detection API is running"
    }


@app.post("/api/v1/detections")
def create_detection(
    detection: DetectionCreate,
    db: Session = Depends(get_db)
):

    detection_event = DetectionEvent(

        video_name=detection.video_name,

        source_id=detection.source_id,

        object_id=detection.object_id,

        object_class=detection.object_class,

        confidence=detection.confidence,

        timestamp=detection.timestamp,

        frame_number=detection.frame_number,

        bbox=detection.bbox,

        # Activity information
        activity=detection.activity,

        activity_start_time=detection.activity_start_time,

        activity_end_time=detection.activity_end_time,

        activity_duration_seconds=detection.activity_duration_seconds,

        json_data=detection.json_data
    )

    db.add(detection_event)

    db.commit()

    db.refresh(detection_event)

    return {
        "message": "Detection stored successfully",
        "id": detection_event.id
    }