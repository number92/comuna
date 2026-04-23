from django.apps import apps
from django.test import SimpleTestCase

from notifications.models import MobilePushDevice, SiteNotification, SiteNotificationPreference


class NotificationsModelsApiTests(SimpleTestCase):
    def test_notifications_app_is_installed(self):
        self.assertTrue(apps.is_installed("notifications"))

    def test_notifications_models_keep_existing_feeds_app_label(self):
        self.assertEqual(MobilePushDevice._meta.app_label, "feeds")
        self.assertEqual(SiteNotification._meta.app_label, "feeds")
        self.assertEqual(SiteNotificationPreference._meta.app_label, "feeds")

    def test_notifications_models_remain_available_through_feeds_app_label(self):
        self.assertIs(apps.get_model("feeds", "MobilePushDevice"), MobilePushDevice)
        self.assertIs(apps.get_model("feeds", "SiteNotification"), SiteNotification)
        self.assertIs(
            apps.get_model("feeds", "SiteNotificationPreference"),
            SiteNotificationPreference,
        )
