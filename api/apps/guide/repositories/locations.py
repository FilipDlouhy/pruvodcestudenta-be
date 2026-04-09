from apps.guide.models import Location
from common.repositories import BaseRepository


class LocationRepository(BaseRepository[Location]):
    """Data access for locations."""

    model = Location
