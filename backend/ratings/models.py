from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class AuthorRatingEvent(models.Model):
    EVENT_TYPE_POST_LIKE = "post_like"
    EVENT_TYPE_COMMENT_LIKE = "comment_like"
    EVENT_TYPE_CHOICES = (
        (EVENT_TYPE_POST_LIKE, "Лайк поста"),
        (EVENT_TYPE_COMMENT_LIKE, "Лайк комментария"),
    )

    author = models.ForeignKey(
        "feeds.Author",
        on_delete=models.CASCADE,
        related_name="rating_events",
    )
    actor = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="author_rating_events",
    )
    post = models.ForeignKey(
        "feeds.Post",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="author_rating_events",
    )
    comment = models.ForeignKey(
        "feeds.PostComment",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="author_rating_events",
    )
    event_type = models.CharField(max_length=32, choices=EVENT_TYPE_CHOICES)
    delta = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "feeds"
        indexes = [
            models.Index(fields=["author", "created_at"]),
            models.Index(fields=["created_at"]),
        ]
        verbose_name = "Изменение рейтинга автора"
        verbose_name_plural = "Изменения рейтинга авторов"

    def __str__(self) -> str:
        return f"{self.author_id}:{self.event_type}:{self.delta}"


__all__ = ["AuthorRatingEvent"]

