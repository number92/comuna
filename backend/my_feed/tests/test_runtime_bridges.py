from django.test import SimpleTestCase

from my_feed import serializers as my_feed_serializers
from my_feed import service as my_feed_service
from my_feed import views as my_feed_views


class MyFeedRuntimeBridgeTests(SimpleTestCase):
    def test_my_feed_views_use_my_feed_runtime(self):
        self.assertIs(
            my_feed_views._serialize_thematic_feed,
            my_feed_serializers._serialize_thematic_feed,
        )
        self.assertIs(
            my_feed_views._serialize_feed_post_card,
            my_feed_serializers._serialize_feed_post_card,
        )
        self.assertIs(
            my_feed_views._thematic_feed_is_moderator,
            my_feed_service._thematic_feed_is_moderator,
        )
        self.assertIs(
            my_feed_views._normalize_thematic_feed_slug,
            my_feed_service._normalize_thematic_feed_slug,
        )
