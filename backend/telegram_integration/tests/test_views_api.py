from django.test import SimpleTestCase
from django.urls import resolve

from telegram_integration.views import telegram_auth, telegram_webhook


class TelegramIntegrationRoutesTests(SimpleTestCase):
    def test_routes_resolve_to_telegram_integration(self):
        self.assertIs(resolve("/api/auth/telegram/").func, telegram_auth)
        self.assertIs(resolve("/tg/webhook/token/").func, telegram_webhook)
