from pathlib import Path
import requests
import sys

from detector import detect_video


if len(sys.argv) < 2:
    print("Video path was not provided.")
    sys.exit(1)


video_path = Path(sys.argv[1])

print("Video path:", video_path)
print("Video exists:", video_path.exists())


if not video_path.exists():

    print("Video file not found!")

else:

    detections = detect_video(str(video_path))

    print("Detection completed!")
    print("Total detections:", len(detections))

    for detection in detections:

        payload = {
            "video_name": video_path.name,
            "source_id": video_path.stem,

            "object_id": detection["object_id"],
            "object_class": detection["object_class"],
            "confidence": detection["confidence"],

            "timestamp": detection.get("timestamp"),

            "frame_number": detection.get(
                "frame_number",
                0
            ),

            "bbox": detection["bbox"],

            # Activity information
            "activity": detection.get(
                "activity",
                "unknown"
            ),

            "activity_start_time": detection.get(
                "activity_start_time"
            ),

            "activity_end_time": detection.get(
                "activity_end_time"
            ),

            "activity_duration_seconds": detection.get(
                "activity_duration_seconds"
            ),

            "json_data": detection
        }

        response = requests.post(
            "http://127.0.0.1:8001/api/v1/detections",
            json=payload
        )

        print(
            "FastAPI:",
            response.status_code,
            response.text
        )
