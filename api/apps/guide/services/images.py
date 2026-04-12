from pathlib import Path

from django.conf import settings
from PIL import Image, ImageOps

from apps.guide.models import FHD_SUFFIX, WEBP_SUFFIX

WEBP_QUALITY = 80  # good size to quality balance for photos
FHD_MAX_WIDTH = 1920  # the fhd variant is never wider than this


class ImageService:
    """Generates and removes the WebP variants stored next to an uploaded image."""

    def sync_variants(self, *, image, folder, slug):
        """Regenerate the variants of a freshly saved image, or remove the files when the image was cleared."""
        if image:
            self._generate_variants(image.path)
        else:
            self.delete_files(folder=folder, slug=slug)

    def delete_files(self, *, folder, slug):
        original = Path(settings.MEDIA_ROOT) / folder / f"{slug}.jpg"
        original.unlink(missing_ok=True)
        Path(str(original) + WEBP_SUFFIX).unlink(missing_ok=True)
        Path(str(original) + FHD_SUFFIX).unlink(missing_ok=True)

    def _generate_variants(self, original_path):
        with Image.open(original_path) as opened:
            picture = ImageOps.exif_transpose(opened)
            if picture.mode not in ("RGB", "RGBA"):
                picture = picture.convert("RGB")
            picture.save(original_path + WEBP_SUFFIX, "WEBP", quality=WEBP_QUALITY)
            if picture.width > FHD_MAX_WIDTH:
                height = round(picture.height * FHD_MAX_WIDTH / picture.width)
                picture = picture.resize((FHD_MAX_WIDTH, height), Image.Resampling.LANCZOS)
            picture.save(original_path + FHD_SUFFIX, "WEBP", quality=WEBP_QUALITY)
