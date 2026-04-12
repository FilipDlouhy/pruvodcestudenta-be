from apps.guide.dtos import DashboardCounts


class DashboardService:
    """Numbers shown on the admin dashboard."""

    def __init__(self, *, section_repository, topic_repository, location_repository):
        self.section_repository = section_repository
        self.topic_repository = topic_repository
        self.location_repository = location_repository

    def get_counts(self):
        return DashboardCounts(
            sections=self.section_repository.count(),
            topics=self.topic_repository.count(),
            locations=self.location_repository.count(),
        )
