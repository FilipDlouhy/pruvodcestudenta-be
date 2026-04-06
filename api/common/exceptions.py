from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


class ApplicationError(Exception):
    """Base class of the errors services raise, the exception handler turns them into JSON responses."""

    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message, *, code=None):
        super().__init__(message)
        self.message = message
        self.code = code

    def to_data(self):
        data = {"detail": self.message}
        if self.code:
            data["code"] = self.code
        return data


class NotFoundError(ApplicationError):
    """The requested resource does not exist."""

    status_code = status.HTTP_404_NOT_FOUND


class ConflictError(ApplicationError):
    """The action is not allowed in the current state of the data."""

    status_code = status.HTTP_409_CONFLICT


class AuthenticationError(ApplicationError):
    """The request has no valid credentials."""

    status_code = status.HTTP_401_UNAUTHORIZED


def custom_exception_handler(exc, context):
    """Turn an ApplicationError into a response, leave everything else to DRF."""
    if not isinstance(exc, ApplicationError):
        return exception_handler(exc, context)
    response = Response(exc.to_data(), status=exc.status_code)
    if isinstance(exc, AuthenticationError):
        response["WWW-Authenticate"] = 'Bearer realm="api"'
    return response
