from .locations import LocationRepository
from .logs import LogMessageRepository
from .sections import SectionRepository
from .topics import TopicRepository

section_repository = SectionRepository()
topic_repository = TopicRepository()
location_repository = LocationRepository()
log_message_repository = LogMessageRepository()

__all__ = ["location_repository", "log_message_repository", "section_repository", "topic_repository"]
