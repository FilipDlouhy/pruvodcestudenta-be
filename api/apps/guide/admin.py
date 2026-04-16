import json

from django import forms
from django.contrib import admin, messages
from django.utils.html import format_html

from apps.guide.models import Location, LogMessage, Section, Topic
from apps.guide.services import location_service, section_service, topic_service
from common.exceptions import ConflictError

admin.site.site_header = "Průvodce studenta UTB"
admin.site.site_title = "Průvodce studenta UTB"
admin.site.index_title = "Správa obsahu"
admin.site.index_template = "guide/admin_index.html"

LOG_CONTEXT_PREVIEW_LENGTH = 100  # characters of the log context shown in the list


class SectionAdminForm(forms.ModelForm):
    """Section form with a color picker."""

    class Meta:
        model = Section
        fields = "__all__"
        widgets = {"color": forms.TextInput(attrs={"type": "color"})}


class ImageAdminMixin:
    """Thumbnail column shared by sections and topics."""

    @admin.display(description="Obrázek")
    def image_preview(self, obj):
        if not obj.image:
            return "-"
        return format_html('<img src="{}" style="height: 40px;">', obj.image.url)


@admin.register(Section)
class SectionAdmin(ImageAdminMixin, admin.ModelAdmin):
    """Admin of sections."""

    form = SectionAdminForm
    list_display = ["title", "image_preview", "slug", "color", "visible", "updated_at"]
    search_fields = ["title", "description"]
    list_per_page = 10
    fields = ["title", "slug", "description", "color", "icon", "image", "visible"]

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ["slug"]
        return []

    def get_prepopulated_fields(self, request, obj=None):
        if obj is not None:
            return {}
        return {"slug": ["title"]}

    def save_model(self, request, obj, form, change):
        section_service.save(section=obj, user=request.user, created=not change, image_changed="image" in form.changed_data)

    def delete_model(self, request, obj):
        try:
            section_service.delete(section=obj, user=request.user)
        except ConflictError:
            self.message_user(request, "Sekci nelze smazat, nejdřív odstraňte její témata.", level=messages.ERROR)

    def delete_queryset(self, request, queryset):
        for section in queryset:
            self.delete_model(request, section)


@admin.register(Topic)
class TopicAdmin(ImageAdminMixin, admin.ModelAdmin):
    """Admin of topics."""

    list_display = ["title", "image_preview", "section", "location", "slug", "url", "visible", "updated_at"]
    list_select_related = ["section", "location"]
    search_fields = ["title", "description"]
    list_per_page = 10
    fields = ["title", "slug", "description", "section", "location", "map_url", "url", "image", "visible", "color"]

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ["slug", "color"]
        return ["color"]

    def get_prepopulated_fields(self, request, obj=None):
        if obj is not None:
            return {}
        return {"slug": ["title"]}

    def save_model(self, request, obj, form, change):
        topic_service.save(topic=obj, user=request.user, created=not change, image_changed="image" in form.changed_data)

    def delete_model(self, request, obj):
        topic_service.delete(topic=obj, user=request.user)

    def delete_queryset(self, request, queryset):
        for topic in queryset:
            self.delete_model(request, topic)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Admin of locations."""

    list_display = ["name", "updated_at"]
    search_fields = ["name"]
    list_per_page = 10
    fields = ["name"]

    def save_model(self, request, obj, form, change):
        location_service.save(location=obj, user=request.user, created=not change)

    def delete_model(self, request, obj):
        try:
            location_service.delete(location=obj, user=request.user)
        except ConflictError:
            self.message_user(request, "Lokalitu nelze smazat, nejdřív odstraňte její témata.", level=messages.ERROR)

    def delete_queryset(self, request, queryset):
        for location in queryset:
            self.delete_model(request, location)


@admin.register(LogMessage)
class LogMessageAdmin(admin.ModelAdmin):
    """Read-only list of the admin change log."""

    list_display = ["id", "level_name", "message", "logged_at", "user_name", "context_preview"]
    list_filter = ["level_name"]
    search_fields = ["message"]
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="Uživatel")
    def user_name(self, obj):
        user = obj.context.get("user")
        if user is None:
            return "-"
        return user.get("username", "-")

    @admin.display(description="Kontext")
    def context_preview(self, obj):
        text = json.dumps(obj.context.get("context"), ensure_ascii=False)
        return text[:LOG_CONTEXT_PREVIEW_LENGTH]
