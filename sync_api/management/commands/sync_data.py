from collections import defaultdict
from datetime import datetime, timezone

from django.core.management.base import BaseCommand

from sync_api.postgres import (
    get_detections,
    mark_as_synced
)

from sync_api.mongo import (
    upsert_video_summary
)


class Command(BaseCommand):

    help = "Synchronize PostgreSQL video data to MongoDB"

    def handle(self, *args, **kwargs):

        rows = get_detections()

        if not rows:
            self.stdout.write(
                self.style.WARNING(
                    "No unsynchronized records found."
                )
            )
            return

        # ---------------------------------------------------------
        # GROUP RECORDS BY VIDEO
        # ---------------------------------------------------------

        videos = defaultdict(list)

        for row in rows:

            video_name = row[1]

            videos[video_name].append(row)

        total_videos = 0
        total_records = 0

        # ---------------------------------------------------------
        # PROCESS EACH VIDEO
        # ---------------------------------------------------------

        for video_name, video_rows in videos.items():

            total_videos += 1

            # -----------------------------------------------------
            # VIDEO DURATION
            # -----------------------------------------------------

            timestamps = [
                row[6]
                for row in video_rows
                if row[6] is not None
            ]

            if timestamps:

                video_start_time = min(timestamps)
                video_end_time = max(timestamps)

                video_duration_seconds = (
                    video_end_time - video_start_time
                ).total_seconds()

            else:

                video_start_time = None
                video_duration_seconds = 0.0

            # -----------------------------------------------------
            # TOTAL DETECTIONS
            # -----------------------------------------------------

            total_detections = len(video_rows)

            # -----------------------------------------------------
            # UNIQUE OBJECTS
            # -----------------------------------------------------

            unique_objects = defaultdict(set)

            for row in video_rows:

                object_class = row[4]
                object_id = row[3]

                if (
                    object_class is not None
                    and object_id is not None
                ):

                    unique_objects[object_class].add(
                        object_id
                    )

            unique_object_counts = {
                object_class: len(object_ids)
                for object_class, object_ids
                in unique_objects.items()
            }

            # -----------------------------------------------------
            # PERSON ACTIVITY INTERVALS
            # -----------------------------------------------------

            person_activity_rows = defaultdict(list)

            for row in video_rows:

                object_id = row[3]
                object_class = row[4]
                activity = row[9]
                activity_start = row[10]
                activity_end = row[11]
                activity_duration = row[12]

                if (
                    object_id is None
                    or object_class != "person"
                    or not activity
                    or activity == "unknown"
                    or activity_start is None
                    or activity_end is None
                    or activity_duration is None
                    or activity_duration < 0.5
                ):
                    continue

                person_activity_rows[object_id].append(
                    {
                        "name": activity,
                        "start": activity_start,
                        "end": activity_end
                    }
                )

            # -----------------------------------------------------
            # MERGE SAME ACTIVITIES WITH SMALL GAPS
            # -----------------------------------------------------

            persons = []

            for object_id, activities in person_activity_rows.items():

                activities.sort(
                    key=lambda item: item["start"]
                )

                merged_activities = []

                for activity in activities:

                    if not merged_activities:

                        merged_activities.append(
                            activity.copy()
                        )
                        continue

                    previous = merged_activities[-1]

                    gap_seconds = (
                        activity["start"]
                        - previous["end"]
                    ).total_seconds()

                    # Merge same activity when the gap is
                    # less than or equal to 0.5 seconds.
                    if (
                        activity["name"] == previous["name"]
                        and gap_seconds <= 0.5
                    ):

                        if activity["end"] > previous["end"]:

                            previous["end"] = activity["end"]

                    else:

                        merged_activities.append(
                            activity.copy()
                        )

                activity_data = []

                for activity in merged_activities:

                    duration_seconds = (
                        activity["end"]
                        - activity["start"]
                    ).total_seconds()

                    if duration_seconds < 0.5:
                        continue

                    activity_data.append(
                        {
                            "name": activity["name"],
                            "start_time": (
                                activity["start"].isoformat()
                            ),
                            "end_time": (
                                activity["end"].isoformat()
                            ),
                            "duration_seconds": round(
                                duration_seconds,
                                2
                            )
                        }
                    )

                if activity_data:

                    persons.append(
                        {
                            "object_id": object_id,
                            "object_class": "person",
                            "activity": activity_data
                        }
                    )

            # -----------------------------------------------------
            # SORT PERSONS
            # -----------------------------------------------------

            persons.sort(
                key=lambda person: person["object_id"]
            )

            # -----------------------------------------------------
            # ACTIVITY SUMMARY
            # Calculate from the CLEANED person activities
            # -----------------------------------------------------

            activity_objects = defaultdict(set)

            for person in persons:

                object_id = person["object_id"]

                for activity in person["activity"]:

                    activity_name = activity["name"]

                    activity_objects[
                        activity_name
                    ].add(object_id)

            activity_summary = {
                activity: len(object_ids)
                for activity, object_ids
                in activity_objects.items()
            }

            # -----------------------------------------------------
            # POSTGRES CREATED TIME
            # -----------------------------------------------------

            created_times = [
                row[14]
                for row in video_rows
                if row[14] is not None
            ]

            if created_times:

                postgres_created_at = min(
                    created_times
                )

            else:

                postgres_created_at = None

            # -----------------------------------------------------
            # MONGODB VIDEO DOCUMENT
            # -----------------------------------------------------

            video_document = {

                "record_type": "video_summary",

                "video_name": video_name,

                "video_duration_seconds": round(
                    max(video_duration_seconds, 0.0),
                    2
                ),

                "summary": {

                    "total_detections":
                        total_detections,

                    "unique_objects":
                        unique_object_counts,

                    "activity_summary":
                        activity_summary
                },

                "persons": persons,

                "postgres_created_at": (
                    postgres_created_at.isoformat()
                    if postgres_created_at
                    else None
                ),

                "synced_at": datetime.now(
                    timezone.utc
                ).isoformat()
            }

            # -----------------------------------------------------
            # CREATE / UPDATE ONE DOCUMENT PER VIDEO
            # -----------------------------------------------------

            mongo_id = upsert_video_summary(
                video_name,
                video_document
            )

            # -----------------------------------------------------
            # MARK POSTGRES RECORDS AS SYNCHRONIZED
            # -----------------------------------------------------

            if mongo_id:

                for row in video_rows:

                    postgres_id = row[0]

                    mark_as_synced(
                        postgres_id
                    )

                    total_records += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Video synchronized: "
                        f"{video_name}"
                    )
                )

                self.stdout.write(
                    f"MongoDB ID: {mongo_id}"
                )

                self.stdout.write(
                    f"Unique objects: "
                    f"{dict(unique_object_counts)}"
                )

                self.stdout.write(
                    f"Persons: {len(persons)}"
                )

        # ---------------------------------------------------------
        # FINAL RESULT
        # ---------------------------------------------------------

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Synchronization completed."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Videos synchronized: {total_videos}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"PostgreSQL records synchronized: "
                f"{total_records}"
            )
        )