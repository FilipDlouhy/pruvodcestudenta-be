from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.guide.dtos import SectionResponseSerializer
from apps.guide.services import page_service


class SectionController(ViewSet):
    """Public API endpoint for a section with its topics."""

    authentication_classes = []
    permission_classes = [AllowAny]
    lookup_field = "slug"
    lookup_value_regex = r"[-\w]+"

    def retrieve(self, request, slug):
        page = page_service.get_section(slug=slug)
        return Response(SectionResponseSerializer(page, context={"request": request}).data)
