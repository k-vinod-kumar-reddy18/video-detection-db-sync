from datetime import datetime, timezone

from django.core.management.base import BaseCommand

from sync_api.postgres import (
    get_detections,
    get_object_totals,
    mark_as_synced
)

from sync_api.mongo import (
    insert_detection,
    detection_collection
)


class Command(BaseCommand):

    help = "Synchronize PostgreSQL data to MongoDB"

    def handle(self, *args, **kwargs):

        # ============================================================
        # GET UNSYNCED POSTGRESQL RECORDS
        # ============================================================

        rows = get_detections()

        synced_count = 0

        # ============================================================
        # SEND ALL DETECTION RECORDS TO MONGODB
        # ============================================================

        for row in rows:

            postgres_id = row[0]

            detection = {
                "record_type": "detection",

                "postgres_id": postgres_id,
                "video_name": row[1],
                "source_id": row[2],
                "object_id": row[3],
                "object_class": row[4],
                "confidence": row[5],

                "timestamp": (
                    row[6].isoformat()
                    if row[6]
                    else None
                ),

                "frame_number": row[7],
                "bbox": row[8],

                "activity": row[9],

                "activity_start_time": (
                    row[10].isoformat()
                    if row[10]
                    else None
                ),

                "activity_end_time": (
                    row[11].isoformat()
                    if row[11]
                    else None
                ),

                "activity_duration_seconds": row[12],

                "json_data": row[13],

                "created_on": (
                    row[14].isoformat()
                    if row[14]
                    else None
                )
            }

            mongo_id = insert_detection(detection)

            if mongo_id:

                mark_as_synced(postgres_id)

                synced_count += 1

        # ============================================================
        # GET UNIQUE OBJECT TOTALS FROM POSTGRESQL
        # ============================================================

        totals = get_object_totals()

        # ============================================================
        # REMOVE OLD SUMMARY RECORD
        # ============================================================

        detection_collection.delete_many({
            "record_type": "summary"
        })

        # ============================================================
        # CREATE NEW SUMMARY RECORD
        # ============================================================

        summary = {
            "record_type": "summary",

            "total_objects": totals,

            "generated_at": datetime.now(
                timezone.utc
            ).isoformat()
        }

        summary_id = insert_detection(summary)

        # ============================================================
        # PRINT RESULT
        # ============================================================

        self.stdout.write(
            self.style.SUCCESS(
                f"Synchronization completed. "
                f"Records synced: {synced_count}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Summary record added: {summary_id}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Total objects: {totals}"
            )
        )