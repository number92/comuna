from django.test import SimpleTestCase
from django.urls import resolve

from my_feed.views import (
    my_feed,
    thematic_feed_manage_detail,
    thematic_feed_posts,
    thematic_feeds_list,
    thematic_feeds_manage,
)


class MyFeedViewsApiTests(SimpleTestCase):
    def test_my_feed_urls_resolve_to_my_feed_app_views(self):
        self.assertIs(resolve("/api/home/my/").func, my_feed)
        self.assertIs(resolve("/api/thematic-feeds/").func, thematic_feeds_list)
        self.assertIs(resolve("/api/thematic-feeds/manage/").func, thematic_feeds_manage)
        self.assertIs(
            resolve("/api/thematic-feeds/manage/demo/").func,
            thematic_feed_manage_detail,
        )
        self.assertIs(
            resolve("/api/thematic-feeds/demo/posts/").func,
            thematic_feed_posts,
        )
