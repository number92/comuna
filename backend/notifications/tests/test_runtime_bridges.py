from django.test import SimpleTestCase

from notifications import serializers as notification_serializers
from notifications import service as notification_service
from notifications import views as notification_views


class NotificationsRuntimeBridgeTests(SimpleTestCase):
    def test_notifications_views_use_notifications_runtime(self):
        self.assertIs(
            notification_views._serialize_site_notification_item,
            notification_serializers._serialize_site_notification_item,
        )

    def test_notifications_service_runtime_exists(self):
        self.assertTrue(callable(notification_service.list_site_notifications_for_user))
