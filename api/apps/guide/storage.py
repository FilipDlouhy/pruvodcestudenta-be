from django.core.files.storage import FileSystemStorage


class OverwriteStorage(FileSystemStorage):
    """File storage that replaces an existing file instead of adding a random suffix to the name."""

    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            self.delete(name)
        return name
