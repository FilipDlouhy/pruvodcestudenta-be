from django.db import transaction

from common.exceptions import ConflictError


class LocationService:
    """Admin actions on locations."""

    def __init__(self, *, location_repository, topic_repository, log_service):
        self.location_repository = location_repository
        self.topic_repository = topic_repository
        self.log_service = log_service

    @transaction.atomic
    def save(self, *, location, user, created):
        self.location_repository.save(location)
        if created:
            message = "Location created"
        else:
            message = "Location updated"
        self.log_service.notice(message=message, model_data=self._log_data(location), user=user)

    @transaction.atomic
    def delete(self, *, location, user):
        if self.topic_repository.exists_for_location(location.pk):
            raise ConflictError("Location has topics, remove them first.")
        model_data = self._log_data(location)
        self.location_repository.delete(location)
        self.log_service.notice(message="Location deleted", model_data=model_data, user=user)

    def _log_data(self, location):
        return {"id": location.pk, "name": location.name}
