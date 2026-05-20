from __future__ import annotations

from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from feeds.models import Post
from special_projects.public_book import (
    DISCUSSION_AUTHOR_TITLE,
    MAX_WORDS,
    PROJECT_SLUG,
    ensure_public_book_discussion_post,
    normalize_public_book_word,
    project_status_for_user,
    schedule_reminder_for_user,
    send_due_reminders,
    submit_word,
)
from special_projects.models import (
    PublicBookBlockedWord,
    PublicBookReminder,
    PublicBookState,
    PublicBookWord,
)
from telegram_integration.models import TelegramAccount
from users.models import VkAccount


User = get_user_model()


class PublicBookTests(TestCase):
    def make_user(self, username: str, *, telegram: bool = False, vk: bool = False):
        user = User.objects.create_user(username=username, password="pass")
        if telegram:
            TelegramAccount.objects.create(
                user=user,
                telegram_id=100000 + user.id,
                username=f"{username}_tg",
            )
        if vk:
            VkAccount.objects.create(
                user=user,
                vk_id=200000 + user.id,
                username=f"{username}_vk",
            )
        return user

    def test_normalize_requires_one_letter_word(self):
        self.assertEqual(
            normalize_public_book_word("Ёлка"),
            {"word": "Ёлка", "normalized_word": "елка"},
        )

        with self.assertRaisesMessage(ValueError, "одно слово"):
            normalize_public_book_word("два слова")
        with self.assertRaisesMessage(ValueError, "только из букв"):
            normalize_public_book_word("слово!")
        with self.assertRaisesMessage(ValueError, "30 символов"):
            normalize_public_book_word("а" * 31)

    def test_submit_word_creates_position_and_updates_status(self):
        user = self.make_user("book-user", telegram=True)

        word = submit_word(user, "Свобода")
        status = project_status_for_user(user)

        self.assertEqual(word.position, 1)
        self.assertEqual(word.word, "Свобода")
        self.assertEqual(word.normalized_word, "свобода")
        self.assertEqual(PublicBookState.objects.get(project_slug=PROJECT_SLUG).total_words, 1)
        self.assertEqual(status["total_words"], 1)
        self.assertFalse(status["can_submit"])
        self.assertTrue(status["telegram_linked"])
        self.assertTrue(status["has_social_identity"])
        self.assertIsNotNone(status["discussion_post"]["id"])

    def test_submit_word_requires_telegram_or_vk_link(self):
        user = User.objects.create_user(username="email-book-user", password="pass")

        status = project_status_for_user(user)
        self.assertFalse(status["can_submit"])
        self.assertEqual(status["submit_block_reason"], "social_required")

        with self.assertRaisesMessage(ValueError, "Telegram или VK"):
            submit_word(user, "Свобода")

    def test_submit_word_allows_vk_link(self):
        user = self.make_user("vk-book-user", vk=True)

        word = submit_word(user, "Голос")

        self.assertEqual(word.position, 1)
        self.assertEqual(word.submitted_by, user)

    def test_submit_word_rejects_blocked_word(self):
        user = self.make_user("blocked-book-user", telegram=True)
        PublicBookBlockedWord.objects.create(word="Запрет")

        with self.assertRaisesMessage(ValueError, "нельзя добавить"):
            submit_word(user, "запрет")

        self.assertFalse(PublicBookWord.objects.exists())

    def test_submit_word_rejects_more_than_one_word_per_24_hours(self):
        user = self.make_user("slow-book-user", telegram=True)
        now = timezone.now()
        first = submit_word(user, "Первое")
        first.created_at = now
        first.save(update_fields=("created_at",))

        with patch("special_projects.public_book.timezone.now", return_value=now + timedelta(hours=23)):
            with self.assertRaisesMessage(ValueError, "24 часа"):
                submit_word(user, "Второе")

        with patch("special_projects.public_book.timezone.now", return_value=now + timedelta(hours=25)):
            second = submit_word(user, "Второе")

        self.assertEqual(second.position, 2)

    def test_submit_word_rejects_full_book(self):
        user = self.make_user("late-book-user", telegram=True)
        PublicBookState.objects.create(project_slug=PROJECT_SLUG, total_words=MAX_WORDS)

        with self.assertRaisesMessage(ValueError, "185000"):
            submit_word(user, "Финиш")

    def test_schedule_reminder_requires_telegram(self):
        user = self.make_user("vk-reminder-user", vk=True)
        submit_word(user, "Слово")

        with self.assertRaisesMessage(ValueError, "Telegram"):
            schedule_reminder_for_user(user)

    def test_schedule_reminder_for_latest_word_and_send_due(self):
        user = self.make_user("reminder-book-user", telegram=True)
        now = timezone.now()
        word = submit_word(user, "Слово")
        word.created_at = now - timedelta(hours=23)
        word.save(update_fields=("created_at",))

        reminder = schedule_reminder_for_user(user)

        self.assertEqual(reminder.scheduled_at, word.created_at + timedelta(hours=24))
        self.assertEqual(PublicBookReminder.objects.count(), 1)

        with patch("notifications.service.send_site_notification_to_telegram") as send_mock:
            sent = send_due_reminders(now=word.created_at + timedelta(hours=24, minutes=1))

        self.assertEqual(sent, 1)
        self.assertTrue(send_mock.called)
        reminder.refresh_from_db()
        self.assertIsNotNone(reminder.sent_at)

    def test_discussion_post_is_public(self):
        post = ensure_public_book_discussion_post()

        self.assertEqual(post.author.title, DISCUSSION_AUTHOR_TITLE)
        self.assertFalse(post.is_pending)
        self.assertFalse(post.is_blocked)
        self.assertEqual(post.raw_data.get("special_project", {}).get("slug"), PROJECT_SLUG)
        self.assertIn("Книга сообщества интернет", post.title)
        self.assertIn(post, Post.objects.filter(is_blocked=False, is_pending=False))
