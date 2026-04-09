from apps.guide.models import Section
from common.repositories import BaseRepository


class SectionRepository(BaseRepository[Section]):
    """Data access for sections."""

    model = Section

    def get_visible_by_slug(self, slug):
        return self.model.objects.filter(slug=slug, visible=True).first()

    def list_visible(self):
        return list(self.model.objects.filter(visible=True))
