from dataclasses import dataclass

from rest_framework import serializers

from .models import User


@dataclass(frozen=True)
class AuthSession:
    """Logged-in user with the tokens to store in cookies."""

    user: User
    access: str
    refresh: str | None


class LoginRequestSerializer(serializers.Serializer):
    """Body of the login request."""

    username = serializers.CharField()
    password = serializers.CharField(style={"input_type": "password"})


class UserResponseSerializer(serializers.Serializer):
    """JSON of a user."""

    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
