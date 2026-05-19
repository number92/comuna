from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from special_projects.film_journey import PROJECT_TIME_ZONE, next_delivery_time, start_subscription
from special_projects.models import FilmJourneyFilm


User = get_user_model()


class FilmJourneyDeliveryTests(TestCase):
    def test_next_delivery_time_keeps_same_time_before_deadline(self):
        now = datetime(2026, 5, 18, 10, 16, tzinfo=PROJECT_TIME_ZONE)

        result = next_delivery_time(now).astimezone(PROJECT_TIME_ZONE)

        self.assertEqual(result, datetime(2026, 5, 19, 10, 16, tzinfo=PROJECT_TIME_ZONE))

    def test_next_delivery_time_caps_after_deadline_at_18_moscow(self):
        now = datetime(2026, 5, 18, 19, 30, tzinfo=PROJECT_TIME_ZONE)

        result = next_delivery_time(now).astimezone(PROJECT_TIME_ZONE)

        self.assertEqual(result, datetime(2026, 5, 19, 18, 0, tzinfo=PROJECT_TIME_ZONE))

    @patch("special_projects.film_journey.create_user_notification")
    def test_start_subscription_delivers_first_film_immediately(self, notify_mock):
        user = User.objects.create_user(username="film-user", password="pass")
        film = FilmJourneyFilm.objects.create(
            title="Первый фильм",
            sort_order=1,
            is_active=True,
        )
        now = datetime(2026, 5, 18, 19, 30, tzinfo=PROJECT_TIME_ZONE)

        with patch("special_projects.film_journey.timezone.now", return_value=now):
            subscription = start_subscription(user)

        entry = subscription.entries.get()
        subscription.refresh_from_db()
        self.assertEqual(entry.film, film)
        self.assertEqual(entry.position, 1)
        self.assertEqual(entry.available_at, now)
        self.assertEqual(entry.notification_sent_at, now)
        self.assertEqual(subscription.last_delivered_at, now)
        self.assertEqual(
            subscription.next_delivery_at.astimezone(PROJECT_TIME_ZONE),
            datetime(2026, 5, 19, 18, 0, tzinfo=PROJECT_TIME_ZONE),
        )
        notify_mock.assert_called_once()
