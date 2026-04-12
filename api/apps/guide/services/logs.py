NOTICE_LEVEL = 250  # Monolog number of the NOTICE level, kept from the Laravel log table


class LogService:
    """Writes the audit log of admin actions."""

    def __init__(self, *, log_message_repository):
        self.log_message_repository = log_message_repository

    def notice(self, *, message, model_data, user):
        """Log an admin action together with the changed model and the acting user."""
        user_data = {
            "id": user.pk,
            "username": user.get_username(),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        self.log_message_repository.create(
            level_name="NOTICE",
            level=NOTICE_LEVEL,
            message=message,
            context={"context": model_data, "user": user_data},
        )
