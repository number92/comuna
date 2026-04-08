from django.apps import apps
from django.test import SimpleTestCase

from editor.models import PostPollVote, PostRatingVote, PostTemplateConfig


class EditorModelsApiTests(SimpleTestCase):
    def test_editor_app_is_installed(self):
        self.assertTrue(apps.is_installed("editor"))

    def test_editor_models_keep_feeds_app_label(self):
        self.assertEqual(PostTemplateConfig._meta.app_label, "feeds")
        self.assertEqual(PostPollVote._meta.app_label, "feeds")
        self.assertEqual(PostRatingVote._meta.app_label, "feeds")

    def test_editor_models_remain_available_through_feeds_app_label(self):
        self.assertIs(apps.get_model("feeds", "PostTemplateConfig"), PostTemplateConfig)
        self.assertIs(apps.get_model("feeds", "PostPollVote"), PostPollVote)
        self.assertIs(apps.get_model("feeds", "PostRatingVote"), PostRatingVote)
