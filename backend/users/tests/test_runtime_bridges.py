from django.test import SimpleTestCase

from feeds import views as feeds_views
from users import serializers as user_serializers
from users import service as user_service
from users import views as user_views


class UsersRuntimeBridgeTests(SimpleTestCase):
    def test_users_views_use_users_runtime_modules(self):
        self.assertIs(user_views._issue_token, user_service._issue_token)
        self.assertIs(user_views._get_user_from_token, user_service._get_user_from_token)
        self.assertIs(user_views._get_user_from_request, user_service._get_user_from_request)
        self.assertIs(user_views._public_user_author_ids, user_service._public_user_author_ids)
        self.assertIs(user_views._serialize_user, user_serializers._serialize_user)
        self.assertIs(
            user_views._serialize_public_site_user_profile,
            user_serializers._serialize_public_site_user_profile,
        )
        self.assertIs(
            user_views._serialize_public_site_user_author_card,
            user_serializers._serialize_public_site_user_author_card,
        )

    def test_feeds_views_bridge_users_runtime(self):
        self.assertIs(feeds_views._issue_token, user_service._issue_token)
        self.assertIs(feeds_views._get_user_from_token, user_service._get_user_from_token)
        self.assertIs(feeds_views._get_user_from_request, user_service._get_user_from_request)
        self.assertIs(feeds_views._public_user_author_ids, user_service._public_user_author_ids)
        self.assertIs(feeds_views._serialize_user, user_serializers._serialize_user)
        self.assertIs(
            feeds_views._serialize_public_site_user_profile,
            user_serializers._serialize_public_site_user_profile,
        )
        self.assertIs(
            feeds_views._serialize_public_site_user_author_card,
            user_serializers._serialize_public_site_user_author_card,
        )
        self.assertIs(feeds_views.register_user, user_views.register_user)
        self.assertIs(feeds_views.login_user, user_views.login_user)
        self.assertIs(feeds_views.auth_me, user_views.auth_me)
        self.assertIs(feeds_views.public_user_profile, user_views.public_user_profile)
        self.assertIs(feeds_views.author_verification_code, user_views.author_verification_code)
        self.assertIs(feeds_views.vk_auth, user_views.vk_auth)
