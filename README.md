# Video Detection and Database Synchronization

A computer vision and backend system that detects and tracks objects from video using YOLO, identifies activities of people, stores detection data in PostgreSQL, and synchronizes the data to MongoDB through Django.

## Project Architecture

Video

↓

YOLO Detection + Tracking

↓

Unique Object ID

↓

Person Pose + Activity Detection

↓

FastAPI

↓

PostgreSQL

↓

Django Synchronization

↓

MongoDB

## Features

- YOLO-based object detection
- Object tracking with unique `object_id`
- Person detection and tracking
- Human pose estimation
- Person activity detection
  - Standing
  - Sitting
  - Bending
  - Walking
  - Moving
- Activity start time
- Activity end time
- Activity duration
- Activity interval merging for continuous/same activities
- PostgreSQL detection storage
- MongoDB synchronization
- Unique object counting by object class
- One MongoDB summary document per video
- Person-wise activity information in MongoDB
- JWT authentication for the backend API
- Automatic synchronization and cleanup

## Technologies Used

- Python
- YOLO / Ultralytics
- OpenCV
- FastAPI
- PostgreSQL
- SQLAlchemy
- Django
- MongoDB
- PyMongo
- Django REST Framework
- JWT
- Git / GitHub

## Database Design

### PostgreSQL

The main table is:

`detection_events`

It stores:

- Detection ID
- Video name
- Source ID
- Object ID
- Object class
- Confidence
- Timestamp
- Frame number
- Bounding box
- Activity
- Activity start time
- Activity end time
- Activity duration
- JSON detection data
- Creation timestamp
- Synchronization status

All person activity information is stored in the same `detection_events` table.

### MongoDB

Database:

`video_detection_db`

Collection:

`detection_events`

MongoDB stores **one summary document for each processed video**.

The document contains:

- Video name
- Video duration
- Total detections
- Unique object totals by class
- Activity summary
- Person-wise activity intervals
- PostgreSQL creation timestamp
- MongoDB synchronization timestamp

Example structure:

```json
{
  "_id": "...",
  "record_type": "video_summary",
  "video_name": "testing_video2.mp4",
  "video_duration_seconds": 17.92,
  "summary": {
    "total_detections": 5361,
    "unique_objects": {
      "person": 9,
      "couch": 1,
      "chair": 3,
      "potted plant": 2,
      "keyboard": 1,
      "tv": 2
    },
    "activity_summary": {
      "sitting": 5,
      "moving": 8,
      "standing": 3,
      "bending": 1
    }
  },
  "persons": [
    {
      "object_id": 1,
      "object_class": "person",
      "activity": [
        {
          "name": "sitting",
          "start_time": "2026-09-25T15:46:37.384027",
          "end_time": "2026-09-25T15:46:55.304027",
          "duration_seconds": 17.92
        }
      ]
    }
  ],
  "postgres_created_at": "...",
  "synced_at": "..."
}
```

The object totals are calculated using unique `object_id` values.

## Project Structure

```text
PostgreSQL-MongoDB-Sync/

│
├── detector.py
├── main.py
├── models.py
├── schemas.py
├── postgres_database.py
├── test_yolo.py
├── run_project.py
├── timer.py
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── sync_project/
│   └── ...
│
└── sync_api/
    ├── postgres.py
    ├── mongo.py
    ├── sync_data.py
    ├── models.py
    ├── views.py
    └── urls.py
```

## Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd PostgreSQL-MongoDB-Sync
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 5. Configure environment variables

Copy:

```text
.env.example
```

to:

```text
.env
```

Then add your PostgreSQL and MongoDB connection details.

Example:

```text
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

MONGO_URI=mongodb://localhost:27017/

MONGO_DB=video_detection_db
```

**Never commit `.env` to GitHub.**

## PostgreSQL Setup

Create the `detection_events` table with the required columns before running the application.

The table stores both raw detection information and person activity information.

Important fields include:

```text
object_id
object_class
confidence
timestamp
frame_number
bbox
activity
activity_start_time
activity_end_time
activity_duration_seconds
is_synced
```

## Run the Project

From the project directory:

```powershell
.\venv\Scripts\python.exe run_project.py
```

The application starts:

```text
FastAPI → http://127.0.0.1:8001

Django  → http://127.0.0.1:8000
```

The program then asks for a video path:

```text
Enter video path:
```

Provide the path to the video file.

Example:

```text
C:\Users\YourName\Downloads\office_video.mp4
```

The video is processed using YOLO detection and tracking.

## Manual Synchronization

To synchronize PostgreSQL data to MongoDB manually:

```powershell
.\venv\Scripts\python.exe manage.py sync_data
```

The synchronization process:

1. Reads unsynchronized detection records from PostgreSQL.
2. Groups records by video.
3. Calculates total detections.
4. Calculates unique object totals using `object_id`.
5. Processes person activity intervals.
6. Removes unknown and extremely short activities.
7. Merges consecutive same activities when the time gap is very small.
8. Calculates the activity summary from the cleaned activities.
9. Creates or updates one MongoDB summary document for each video.
10. Marks successfully synchronized PostgreSQL records.

## Object Counting

Object totals are calculated using unique object IDs.

For example, if:

```text
person object_id = 1
```

appears in 500 video frames, it is counted as:

```text
one person
```

not:

```text
500 people
```

This prevents the same tracked person from being counted multiple times.

## Activity Recognition

Activity recognition is currently applied to detected people.

The system uses:

- YOLO pose estimation
- Person bounding-box movement
- Movement between video frames

to estimate activities such as:

```text
standing
sitting
bending
walking
moving
```

Other objects are detected and tracked but do not receive human activity labels.

### Activity Intervals

Each person's activity is stored with:

```text
activity name
start time
end time
duration
```

Very short activity intervals are filtered out.

When the same activity continues with only a very small gap between intervals, the intervals are merged into a single activity period.

For example:

```text
sitting
15:46:37 → 15:46:45

sitting
15:46:45 → 15:46:55
```

can be combined into:

```text
sitting
15:46:37 → 15:46:55
```

This produces cleaner activity information in MongoDB.

## API

FastAPI provides the detection storage API.

Example:

```text
POST /api/v1/detections
```

Django provides the synchronization and MongoDB API functionality.

JWT authentication endpoints are available through:

```text
/api/token/

/api/token/refresh/
```

## Automatic Synchronization and Cleanup

The project includes an automatic synchronization process using `timer.py`.

The timer:

1. Runs the PostgreSQL → MongoDB synchronization.
2. Runs the cleanup process.
3. Waits for the configured interval.
4. Repeats the process.

The current timer runs synchronization every 2 minutes.

The cleanup process removes old synchronized PostgreSQL records according to the configured cleanup period.

## Verification

After synchronization, MongoDB can be checked using:

```javascript
use video_detection_db

db.detection_events.findOne(
    { video_name: "testing_video2.mp4" }
)
```

To check the number of documents:

```javascript
db.detection_events.countDocuments()
```

The expected design is **one MongoDB document per processed video**.

## Git Workflow

Check the current status:

```powershell
git status
```

Add changes:

```powershell
git add .
```

Commit changes:

```powershell
git commit -m "Update synchronization logic"
```

Push to GitHub:

```powershell
git push origin main
```

## Future Improvements

- More advanced human activity recognition
- Better temporal activity classification
- Improved multi-person activity tracking
- Real-time camera / RTSP processing
- Dashboard for detection and activity analytics
- Improved MongoDB reporting
- Production deployment using Docker