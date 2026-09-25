import os

import psycopg2
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_postgres_connection():
    return psycopg2.connect(DATABASE_URL)


# ============================================================
# GET UNSYNCED DETECTION RECORDS
# ============================================================

def get_detections():
    conn = get_postgres_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            video_name,
            source_id,
            object_id,
            object_class,
            confidence,
            timestamp,
            frame_number,
            bbox,
            activity,
            activity_start_time,
            activity_end_time,
            activity_duration_seconds,
            json_data,
            created_on
        FROM detection_events
        WHERE is_synced = FALSE
        ORDER BY id;
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows


# ============================================================
# GET UNIQUE OBJECT TOTALS
# ============================================================

def get_object_totals():
    conn = get_postgres_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            object_class,
            COUNT(DISTINCT object_id) AS total_objects
        FROM detection_events
        WHERE object_id IS NOT NULL
        GROUP BY object_class
        ORDER BY object_class;
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    totals = {}

    for object_class, total_objects in rows:
        totals[object_class] = total_objects

    return totals


# ============================================================
# MARK RECORD AS SYNCED
# ============================================================

def mark_as_synced(postgres_id):
    conn = get_postgres_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE detection_events
        SET is_synced = TRUE
        WHERE id = %s;
    """, (postgres_id,))

    conn.commit()

    cursor.close()
    conn.close()


# ============================================================
# DELETE OLD SYNCED RECORDS
# ============================================================

def delete_old_synced_detections():
    conn = get_postgres_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM detection_events
        WHERE is_synced = TRUE
        AND created_on <= (NOW() AT TIME ZONE 'UTC') - INTERVAL '2 hours';
    """)

    deleted_count = cursor.rowcount

    conn.commit()

    cursor.close()
    conn.close()

    return deleted_count