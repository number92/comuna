from django.apps import apps
from django.test import SimpleTestCase

from ratings.models import AuthorRatingEvent


class RatingsModelsApiTests(SimpleTestCase):
    def test_ratings_app_is_installed(self):
        self.assertTrue(apps.is_installed("ratings"))

    def test_ratings_models_keep_existing_feeds_app_label(self):
        self.assertEqual(AuthorRatingEvent._meta.app_label, "feeds")

    def test_ratings_models_remain_available_through_feeds_app_label(self):
        self.assertIs(apps.get_model("feeds", "AuthorRatingEvent"), AuthorRatingEvent)
