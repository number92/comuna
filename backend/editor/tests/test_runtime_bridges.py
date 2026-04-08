from django.test import SimpleTestCase

from editor import serializers as editor_serializers
from editor import service as editor_service
from editor import views as editor_views


class EditorRuntimeBridgeTests(SimpleTestCase):
    def test_editor_views_use_editor_serializer_runtime(self):
        self.assertIs(editor_views._serialize_post_for_user, editor_serializers._serialize_post_for_user)
        self.assertIs(editor_views._serialize_post_rating_block, editor_serializers._serialize_post_rating_block)
        self.assertIs(editor_views._serialize_post_ratings, editor_serializers._serialize_post_ratings)
        self.assertIs(editor_views._normalize_post_template_payload, editor_service._normalize_post_template_payload)
