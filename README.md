# Video Detection and Database Synchronization

A computer vision and backend system that detects and tracks objects from video using YOLO, identifies activities of people, stores detection data in PostgreSQL, and synchronizes the data to MongoDB through Django.

## Project Architecture

```text
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
Features
YOLO-based object detection
Object tracking with unique object_id
Person detection and tracking
Human pose estimation
Person activity detection
Standing
Sitting
Bending
Walking
Moving
Activity start time
Activity end time
Activity duration
PostgreSQL detection storage
MongoDB synchronization
Unique object counting by object class
MongoDB summary record
JWT authentication for the backend API
Automatic synchronization and cleanup
Technologies Used
Python
YOLO / Ultralytics
OpenCV
FastAPI
PostgreSQL
SQLAlchemy
Django
MongoDB
PyMongo
Django REST Framework
JWT
Git / GitHub
Database Design
PostgreSQL

The main table is:

detection_events

It stores:

Detection ID
Video name
Source ID
Object ID
Object class
Confidence
Timestamp
Frame number
Bounding box
Activity
Activity start time
Activity end time
Activity duration
JSON detection data
Creation timestamp
Synchronization status
MongoDB

Database:

video_detection_db

Collection:

detection_events

MongoDB stores the PostgreSQL detection records and an additional summary document containing unique object totals by class.

Example:

{
  "record_type": "summary",
  "total_objects": {
    "person": 9,
    "chair": 3,
    "couch": 1,
    "keyboard": 1,
    "potted plant": 2,
    "tv": 2
  }
}

The object totals are calculated using unique object_id values.

Project Structure
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
Setup
1. Clone the Repository
git clone https://github.com/k-vinod-kumar-reddy18/video-detection-db-sync.git
cd PostgreSQL-MongoDB-Sync
2. Create a Virtual Environment
python -m venv venv
3. Activate the Virtual Environment

Windows PowerShell:

.\venv\Scripts\Activate.ps1
4. Install Dependencies
python -m pip install -r requirements.txt
5. Configure Environment Variables

Copy:

.env.example

to:

.env

Then add your PostgreSQL and MongoDB connection details.

Example:

DATABASE_URL=postgresql://username:password@localhost:5432/database_name

MONGO_URI=mongodb://localhost:27017/

MONGO_DB=video_detection_db
PostgreSQL Setup

Create the detection_events table with the required columns before running the application.

The table stores both raw detection information and person activity information.

Run the Project

From the project directory:

.\venv\Scripts\python.exe run_project.py

The application starts:

FastAPI → http://127.0.0.1:8001

Django  → http://127.0.0.1:8000

The program then asks for a video path:

Enter video path:

Provide the path to the video file.

Example:

C:\Users\YourName\Downloads\office_video.mp4
Manual Synchronization

To synchronize PostgreSQL data to MongoDB manually:

.\venv\Scripts\python.exe manage.py sync_data

The synchronization process:

Reads unsynchronized detection records from PostgreSQL.
Inserts detection records into MongoDB.
Marks successfully synchronized PostgreSQL records.
Calculates unique object totals.
Creates or updates the MongoDB summary record.
Object Counting

Object totals are calculated using unique object IDs.

For example, if:

person object_id = 1

appears in 500 video frames, it is counted as one person, not 500 people.

Activity Recognition

Activity recognition is currently applied to detected people.

The system uses pose information and movement between frames to estimate activities such as:

standing
sitting
bending
walking
moving

Other objects are detected and tracked but do not receive human activity labels.

API

FastAPI provides the detection storage API.

Example:

POST /api/v1/detections

Django provides the synchronization and MongoDB API functionality.

JWT authentication endpoints are available through:

/api/token/

/api/token/refresh/
Automatic Synchronization and Cleanup

The project includes an automatic timer that:

Synchronizes PostgreSQL detection records to MongoDB.
Updates the MongoDB summary.
Cleans up synchronized PostgreSQL records based on the configured cleanup period.
Repeats the process automatically.

The current synchronization interval is:

2 minutes

The cleanup period is:

2 hours
Future Improvements
More advanced human activity recognition
Better temporal activity classification
Improved multi-person activity tracking
Real-time camera/RTSP processing
Dashboard for detection and activity analytics
Improved MongoDB reporting
Production deployment using Docker