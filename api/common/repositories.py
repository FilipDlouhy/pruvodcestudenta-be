from django.db.models import Model


class BaseRepository[T: Model]:
    """Basic data access shared by all repositories, the only place that talks to Model.objects."""

    model: type[T]

    def get_by_id(self, pk) -> T | None:
        return self.model.objects.filter(pk=pk).first()

    def count(self) -> int:
        return self.model.objects.count()

    def save(self, instance: T) -> None:
        instance.save()

    def delete(self, instance: T) -> None:
        instance.delete()
