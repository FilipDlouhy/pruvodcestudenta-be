from apps.guide.models import LogMessage
from common.repositories import BaseRepository


class LogMessageRepository(BaseRepository[LogMessage]):
    """Data access for the admin audit log."""

    model = LogMessage

    def create(self, *, level_name, level, message, context):
        return self.model.objects.create(level_name=level_name, level=level, message=message, context=context)
