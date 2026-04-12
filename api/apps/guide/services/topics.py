from django.db import transaction


class TopicService:
    """Admin actions on topics."""

    def __init__(self, *, topic_repository, image_service, log_service):
        self.topic_repository = topic_repository
        self.image_service = image_service
        self.log_service = log_service

    @transaction.atomic
    def save(self, *, topic, user, created, image_changed):
        if created:
            topic.color = topic.section.color
        self.topic_repository.save(topic)
        if image_changed:
            self.image_service.sync_variants(image=topic.image, folder=topic.IMAGE_FOLDER, slug=topic.slug)
        if created:
            message = "Topic created"
        else:
            message = "Topic updated"
        self.log_service.notice(message=message, model_data=self._log_data(topic), user=user)

    @transaction.atomic
    def delete(self, *, topic, user):
        model_data = self._log_data(topic)
        folder = topic.IMAGE_FOLDER
        slug = topic.slug
        self.topic_repository.delete(topic)
        # files are removed only after the delete is committed
        transaction.on_commit(lambda: self.image_service.delete_files(folder=folder, slug=slug))
        self.log_service.notice(message="Topic deleted", model_data=model_data, user=user)

    def _log_data(self, topic):
        return {
            "id": topic.pk,
            "title": topic.title,
            "description": topic.description,
            "slug": topic.slug,
            "color": topic.color,
            "url": topic.url,
            "map_url": topic.map_url,
            "section_id": topic.section_id,
            "location_id": topic.location_id,
            "visible": topic.visible,
            "image": topic.image.name,
        }
