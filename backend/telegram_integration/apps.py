from django.apps import AppConfig
from django.conf import settings


class TelegramIntegrationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "telegram_integration"
    verbose_name = "Telegram"

    def ready(self) -> None:
        if settings.TELEGRAM_USE_POLLING:
            from .polling import start_polling_thread

            start_polling_thread()

