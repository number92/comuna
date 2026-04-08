from django.apps import apps
from django.test import SimpleTestCase

from feeds.models import (
    AuthorAdmin as FeedsAuthorAdmin,
    AuthorVerificationCode as FeedsAuthorVerificationCode,
    SiteUserProfile as FeedsSiteUserProfile,
    VkAccount as FeedsVkAccount,
)
from users.models import (
    AuthorAdmin,
    AuthorVerificationCode,
    SiteUserProfile,
    TelegramAccount,
    VkAccount,
)


class UsersModelsApiTests(SimpleTestCase):
    def test_users_app_is_installed(self):
        self.assertTrue(apps.is_installed("users"))

    def test_users_models_keep_existing_feeds_app_label(self):
        self.assertEqual(AuthorAdmin._meta.app_label, "feeds")
        self.assertEqual(AuthorVerificationCode._meta.app_label, "feeds")
        self.assertEqual(TelegramAccount._meta.app_label, "feeds")
        self.assertEqual(VkAccount._meta.app_label, "feeds")
        self.assertEqual(SiteUserProfile._meta.app_label, "feeds")

    def test_users_models_reexport_existing_feeds_models(self):
        self.assertIs(AuthorAdmin, FeedsAuthorAdmin)
        self.assertIs(AuthorVerificationCode, FeedsAuthorVerificationCode)
        self.assertIs(TelegramAccount, apps.get_model("feeds", "TelegramAccount"))
        self.assertIs(VkAccount, FeedsVkAccount)
        self.assertIs(SiteUserProfile, FeedsSiteUserProfile)
