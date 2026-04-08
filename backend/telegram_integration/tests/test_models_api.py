from django.apps import apps
from django.test import SimpleTestCase

from telegram_integration.models import BotSession, TelegramAccount
from users.models import TelegramAccount as UsersTelegramAccount


class TelegramIntegrationModelsApiTests(SimpleTestCase):
    def test_app_is_installed(self):
        self.assertTrue(apps.is_installed("telegram_integration"))

    def test_models_keep_feeds_app_label(self):
        self.assertEqual(TelegramAccount._meta.app_label, "feeds")
        self.assertEqual(BotSession._meta.app_label, "feeds")

    def test_models_remain_available_via_feeds_app_label(self):
        self.assertIs(UsersTelegramAccount, TelegramAccount)
        self.assertIs(apps.get_model("feeds", "BotSession"), BotSession)
