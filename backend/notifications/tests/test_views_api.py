from django.test import SimpleTestCase
from django.urls import resolve

from notifications.views import (
    auth_notification_read,
    auth_notification_settings,
    auth_notifications,
    auth_notifications_read_all,
)


class NotificationsViewsApiTests(SimpleTestCase):
    def test_notification_urls_resolve_to_notifications_app_views(self):
        self.assertIs(resolve("/api/auth/notifications/").func, auth_notifications)
        self.assertIs(
            resolve("/api/auth/notifications/settings/").func,
            auth_notification_settings,
        )
        self.assertIs(
            resolve("/api/auth/notifications/read-all/").func,
            auth_notifications_read_all,
        )
        self.assertIs(
            resolve("/api/auth/notifications/42/read/").func,
            auth_notification_read,
        )
