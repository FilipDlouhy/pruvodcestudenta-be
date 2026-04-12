from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.guide.dtos import TopicResponseSerializer
from apps.guide.services import page_service


class TopicController(ViewSet):
    """Public API endpoint for a single topic."""

    authentication_classes = []
    permission_classes = [AllowAny]
    lookup_field = "slug"
    lookup_value_regex = r"[-\w]+"

    def retrieve(self, request, slug):
        topic = page_service.get_topic(slug=slug)
        return Response(TopicResponseSerializer(topic, context={"request": request}).data)
