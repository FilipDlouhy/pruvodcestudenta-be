from dataclasses import dataclass

from rest_framework import serializers

from .models import Section, Topic


def absolute_media_url(request, path):
    """Absolute URL of a media file path, empty string when the path is empty."""
    if path == "":
        return ""
    return request.build_absolute_uri(path)


@dataclass(frozen=True)
class SectionPage:
    """A section together with its visible topics."""

    section: Section
    topics: list[Topic]


@dataclass(frozen=True)
class LandingPage:
    """The visible sections shown on the landing page."""

    sections: list[SectionPage]


@dataclass(frozen=True)
class SearchTopic:
    """One topic found by the search."""

    title: str
    slug: str
    section_slug: str
    color: str


@dataclass(frozen=True)
class SearchResult:
    """Topics found by the search."""

    topics: list[SearchTopic]


@dataclass(frozen=True)
class DashboardCounts:
    """Numbers shown on the admin dashboard."""

    sections: int
    topics: int
    locations: int


@dataclass(frozen=True)
class SeedResult:
    """How many rows the seed command created."""

    section_count: int
    location_count: int


class LandingSearchRequestSerializer(serializers.Serializer):
    """Body of the landing page search."""

    query = serializers.CharField()
    sections = serializers.ListField(child=serializers.IntegerField(), default=list)
    locations = serializers.ListField(child=serializers.IntegerField(), default=list)


class TopicResponseSerializer(serializers.Serializer):
    """JSON of a topic, same keys and order as the Laravel TopicResponse."""

    title = serializers.CharField()
    description = serializers.CharField()
    url = serializers.CharField()
    slug = serializers.CharField()
    image = serializers.SerializerMethodField()
    color = serializers.CharField()
    location = serializers.CharField(source="map_url")

    def get_image(self, topic):
        return absolute_media_url(self.context["request"], topic.fhd_image_url)


class SectionResponseSerializer(serializers.Serializer):
    """JSON of a section page with its topics, same keys and order as the Laravel SectionResponse."""

    title = serializers.CharField(source="section.title")
    description = serializers.CharField(source="section.description")
    slug = serializers.CharField(source="section.slug")
    image = serializers.SerializerMethodField()
    color = serializers.CharField(source="section.color")
    icon = serializers.CharField(source="section.icon")
    topics = TopicResponseSerializer(many=True)

    def get_image(self, page):
        return absolute_media_url(self.context["request"], page.section.fhd_image_url)


class LandingResponseSerializer(serializers.Serializer):
    """JSON of the landing page."""

    sections = SectionResponseSerializer(many=True)


class SearchTopicResponseSerializer(serializers.Serializer):
    """JSON of one search hit."""

    title = serializers.CharField()
    slug = serializers.CharField()
    sectionSlug = serializers.CharField(source="section_slug")
    color = serializers.CharField()


class SearchResponseSerializer(serializers.Serializer):
    """JSON of the search result."""

    topics = SearchTopicResponseSerializer(many=True)
