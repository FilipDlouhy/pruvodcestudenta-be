from apps.guide.dtos import LandingPage, SearchResult, SearchTopic, SectionPage
from common.exceptions import NotFoundError


class PageService:
    """Public read-only pages of the guide, only visible content is returned."""

    def __init__(self, *, section_repository, topic_repository):
        self.section_repository = section_repository
        self.topic_repository = topic_repository

    def get_landing(self):
        sections = self.section_repository.list_visible()
        return LandingPage(sections=[SectionPage(section=section, topics=[]) for section in sections])

    def get_section(self, *, slug):
        section = self.section_repository.get_visible_by_slug(slug)
        if section is None:
            raise NotFoundError("Section not found.")
        topics = self.topic_repository.list_visible_by_section(section.pk)
        return SectionPage(section=section, topics=topics)

    def get_topic(self, *, slug):
        topic = self.topic_repository.get_visible_by_slug(slug)
        if topic is None:
            raise NotFoundError("Topic not found.")
        return topic

    def search(self, *, query, section_ids, location_ids):
        topics = self.topic_repository.search_visible(query, section_ids, location_ids)
        found = [
            SearchTopic(title=topic.title, slug=topic.slug, section_slug=topic.section.slug, color=topic.color)
            for topic in topics
        ]
        return SearchResult(topics=found)
