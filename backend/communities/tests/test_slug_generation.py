from django.contrib.auth import get_user_model
from django.test import TestCase

from communities.models import Comun
from communities.views import _generate_unique_comun_slug, _normalize_comun_slug

User = get_user_model()


class CommunitiesSlugGenerationTests(TestCase):
    def test_normalize_comun_slug_transliterates_russian_name(self):
        self.assertEqual(_normalize_comun_slug("Тестовое сообщество"), "testovoe-soobshchestvo")

    def test_generate_unique_comun_slug_uses_transliteration_and_suffix(self):
        creator = User.objects.create_user(username="slug-owner")
        Comun.objects.create(
            name="Тестовое сообщество",
            slug="testovoe-soobshchestvo",
            creator=creator,
        )

        self.assertEqual(
            _generate_unique_comun_slug("Тестовое сообщество"),
            "testovoe-soobshchestvo-2",
        )
