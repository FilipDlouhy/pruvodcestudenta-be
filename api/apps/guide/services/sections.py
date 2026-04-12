from django.db import transaction

from common.exceptions import ConflictError


class SectionService:
    """Admin actions on sections."""

    def __init__(self, *, section_repository, topic_repository, image_service, log_service):
        self.section_repository = section_repository
        self.topic_repository = topic_repository
        self.image_service = image_service
        self.log_service = log_service

    @transaction.atomic
    def save(self, *, section, user, created, image_changed):
        self.section_repository.save(section)
        if image_changed:
            self.image_service.sync_variants(image=section.image, folder=section.IMAGE_FOLDER, slug=section.slug)
        if created:
            message = "Section created"
        else:
            message = "Section updated"
        self.log_service.notice(message=message, model_data=self._log_data(section), user=user)

    @transaction.atomic
    def delete(self, *, section, user):
        if self.topic_repository.exists_for_section(section.pk):
            raise ConflictError("Section has topics, remove them first.")
        model_data = self._log_data(section)
        folder = section.IMAGE_FOLDER
        slug = section.slug
        self.section_repository.delete(section)
        # files are removed only after the delete is committed
        transaction.on_commit(lambda: self.image_service.delete_files(folder=folder, slug=slug))
        self.log_service.notice(message="Section deleted", model_data=model_data, user=user)

    def _log_data(self, section):
        return {
            "id": section.pk,
            "title": section.title,
            "description": section.description,
            "slug": section.slug,
            "color": section.color,
            "icon": section.icon,
            "visible": section.visible,
            "image": section.image.name,
        }
