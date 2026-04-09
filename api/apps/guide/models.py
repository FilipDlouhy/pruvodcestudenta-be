from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from .storage import OverwriteStorage

DEFAULT_COLOR = "#FF9F63"  # fallback color of a new section
WEBP_SUFFIX = ".webp"  # full-size variant, appended to the original file name
FHD_SUFFIX = ".fhd.webp"  # variant at most 1920 px wide, served by the public API

color_validator = RegexValidator(r"^#[0-9a-fA-F]{6}$", "Zadejte barvu ve formátu #RRGGBB.")


def image_upload_path(instance, filename):
    """Uploads are always stored as <folder>/<slug>.jpg, same as in the original Laravel app."""
    return f"{instance.IMAGE_FOLDER}/{instance.slug}.jpg"


class ContentItem(models.Model):
    """Fields shared by sections and topics."""

    IMAGE_FOLDER: str

    title = models.CharField("Název", max_length=255)
    description = models.TextField("Popis (HTML)", blank=True)
    slug = models.SlugField("Slug", max_length=255, unique=True, help_text="Musí být unikátní a po vytvoření ho nelze změnit.")
    visible = models.BooleanField("Zobrazit na webu", default=True)
    image = models.ImageField("Obrázek", upload_to=image_upload_path, storage=OverwriteStorage(), max_length=255, blank=True)
    created_at = models.DateTimeField("Vytvořeno", auto_now_add=True)
    updated_at = models.DateTimeField("Upraveno", auto_now=True)

    class Meta:
        abstract = True
        ordering = ["id"]

    def __str__(self):
        return self.title

    @property
    def fhd_image_url(self):
        """Relative URL of the 1920 px WebP variant, empty when there is no image."""
        if not self.image:
            return ""
        return self.image.url + FHD_SUFFIX


class Section(ContentItem):
    """Top-level category of the guide, groups topics."""

    IMAGE_FOLDER = "sections"

    color = models.CharField("Barva", max_length=7, default=DEFAULT_COLOR, validators=[color_validator])
    icon = models.CharField("Ikona (URL)", max_length=255, blank=True)

    class Meta(ContentItem.Meta):
        verbose_name = "Sekce"
        verbose_name_plural = "Sekce"


class Location(models.Model):
    """City where a topic is located, also a filter of the search."""

    name = models.CharField("Název", max_length=255)
    created_at = models.DateTimeField("Vytvořeno", auto_now_add=True)
    updated_at = models.DateTimeField("Upraveno", auto_now=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "Lokalita"
        verbose_name_plural = "Lokality"

    def __str__(self):
        return self.name


class Topic(ContentItem):
    """Article of the guide that belongs to one section and one city."""

    IMAGE_FOLDER = "topics"

    section = models.ForeignKey(Section, on_delete=models.PROTECT, related_name="topics", verbose_name="Sekce")
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="topics", verbose_name="Lokalita")
    # copied from the section when the topic is created and never synced afterwards
    color = models.CharField("Barva", max_length=7, blank=True, validators=[color_validator])
    url = models.URLField("Odkaz na web", max_length=1000, blank=True)
    map_url = models.URLField("URL mapy (Google Maps embed)", max_length=1000, blank=True)

    class Meta(ContentItem.Meta):
        verbose_name = "Téma"
        verbose_name_plural = "Témata"


class LogMessage(models.Model):
    """Audit log of admin actions, written by LogService."""

    level_name = models.CharField("Úroveň", max_length=255)
    level = models.PositiveSmallIntegerField("Číslo úrovně")
    message = models.CharField("Akce", max_length=255)
    logged_at = models.DateTimeField("Zaznamenáno", default=timezone.now)
    context = models.JSONField("Kontext", default=dict)
    extra = models.JSONField("Extra", default=dict)

    class Meta:
        ordering = ["-logged_at", "-id"]
        verbose_name = "Záznam logu"
        verbose_name_plural = "Logy"

    def __str__(self):
        return f"{self.level_name} {self.message}"
