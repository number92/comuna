from django.apps import apps
from django.test import SimpleTestCase

from my_feed.models import ThematicFeed


class MyFeedModelsApiTests(SimpleTestCase):
    def test_my_feed_app_is_installed(self):
        self.assertTrue(apps.is_installed("my_feed"))

    def test_thematic_feed_model_keeps_existing_feeds_app_label(self):
        self.assertEqual(ThematicFeed._meta.app_label, "feeds")

    def test_thematic_feed_remains_available_through_feeds_app_label(self):
        self.assertIs(apps.get_model("feeds", "ThematicFeed"), ThematicFeed)
