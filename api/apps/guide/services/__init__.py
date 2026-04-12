from apps.guide.repositories import location_repository, log_message_repository, section_repository, topic_repository

from .dashboard import DashboardService
from .images import ImageService
from .locations import LocationService
from .logs import LogService
from .pages import PageService
from .sections import SectionService
from .seed import SeedService
from .topics import TopicService

image_service = ImageService()
log_service = LogService(log_message_repository=log_message_repository)
page_service = PageService(section_repository=section_repository, topic_repository=topic_repository)
section_service = SectionService(
    section_repository=section_repository,
    topic_repository=topic_repository,
    image_service=image_service,
    log_service=log_service,
)
topic_service = TopicService(topic_repository=topic_repository, image_service=image_service, log_service=log_service)
location_service = LocationService(
    location_repository=location_repository,
    topic_repository=topic_repository,
    log_service=log_service,
)
dashboard_service = DashboardService(
    section_repository=section_repository,
    topic_repository=topic_repository,
    location_repository=location_repository,
)
seed_service = SeedService(section_repository=section_repository, location_repository=location_repository)

__all__ = [
    "dashboard_service",
    "location_service",
    "page_service",
    "section_service",
    "seed_service",
    "topic_service",
]
