from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.viewsets import ViewSet

from apps.guide.dtos import LandingResponseSerializer, LandingSearchRequestSerializer, SearchResponseSerializer
from apps.guide.services import page_service


class LandingController(ViewSet):
    """Public API endpoints for the landing page and the topic search."""

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_scope = "public"

    def list(self, request):
        landing = page_service.get_landing()
        return Response(LandingResponseSerializer(landing, context={"request": request}).data)

    @action(detail=False, methods=["post"], throttle_classes=[ScopedRateThrottle])
    def search(self, request):
        serializer = LandingSearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        result = page_service.search(query=data["query"], section_ids=data["sections"], location_ids=data["locations"])
        return Response(SearchResponseSerializer(result).data)
