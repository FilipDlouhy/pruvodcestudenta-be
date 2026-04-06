from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class AccountAdmin(UserAdmin):
    """Admin of user accounts."""

    list_display = ["username", "email", "first_name", "last_name", "is_staff"]
