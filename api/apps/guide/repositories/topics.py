from django.db.models import Q

from apps.guide.models import Topic
from common.repositories import BaseRepository


class TopicRepository(BaseRepository[Topic]):
    """Data access for topics."""

    model = Topic

    def get_visible_by_slug(self, slug):
        """Get a visible topic whose section is visible too."""
        return self.model.objects.filter(slug=slug, visible=True, section__visible=True).first()

    def list_visible_by_section(self, section_id):
        return list(self.model.objects.filter(section_id=section_id, visible=True))

    def search_visible(self, query, section_ids, location_ids):
        """Find visible topics of visible sections whose title or description contains the query."""
        topics = self.model.objects.filter(visible=True, section__visible=True).select_related("section")
        if section_ids:
            topics = topics.filter(section_id__in=section_ids)
        if location_ids:
            topics = topics.filter(location_id__in=location_ids)
        topics = topics.filter(Q(title__icontains=query) | Q(description__icontains=query))
        return list(topics)

    def exists_for_section(self, section_id):
        return self.model.objects.filter(section_id=section_id).exists()

    def exists_for_location(self, location_id):
        return self.model.objects.filter(location_id=location_id).exists()
