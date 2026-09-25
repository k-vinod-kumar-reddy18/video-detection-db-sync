from django.core.management.base import BaseCommand

from sync_api.postgres import delete_old_synced_detections


class Command(BaseCommand):

    help = "Delete PostgreSQL records that were synced to MongoDB more than 2 hours ago"

    def handle(self, *args, **kwargs):

        deleted_count = delete_old_synced_detections()

        self.stdout.write(
            self.style.SUCCESS(
                f"Cleanup completed. Records deleted: {deleted_count}"
            )
        )