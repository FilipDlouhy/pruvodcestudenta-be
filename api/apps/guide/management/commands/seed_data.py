from django.core.management.base import BaseCommand

from apps.guide.services import seed_service


class Command(BaseCommand):
    help = "Load the reference locations and sections into empty tables. Safe to run repeatedly."

    def handle(self, *args, **options):
        seeded = seed_service.seed_reference_data()
        self.stdout.write(
            self.style.SUCCESS(f"Seeded {seeded.location_count} locations and {seeded.section_count} sections.")
        )
