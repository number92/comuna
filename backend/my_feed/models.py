from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class ThematicFeed(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    moderators = models.ManyToManyField(
        User,
        blank=True,
        related_name="thematic_feed_moderation",
        help_text="Пользователи, которые могут редактировать состав папки.",
    )
    authors = models.ManyToManyField(
        "feeds.Author",
        blank=True,
        related_name="thematic_feeds",
        help_text="Авторы, посты которых будут показаны в тематической ленте.",
    )
    excluded_authors = models.ManyToManyField(
        "feeds.Author",
        blank=True,
        related_name="thematic_feeds_excluded",
        help_text="Авторы, посты которых будут исключены из папки.",
    )
    rubrics = models.ManyToManyField(
        "feeds.Rubric",
        blank=True,
        related_name="thematic_feeds_included",
        verbose_name="Рубрики",
        help_text="Посты этих рубрик будут добавляться в папку.",
    )
    tags = models.ManyToManyField(
        "feeds.Tag",
        blank=True,
        related_name="thematic_feeds_included",
        verbose_name="Теги",
        help_text="Посты с этими тегами будут добавляться в папку.",
    )
    blocked_tags = models.ManyToManyField(
        "feeds.Tag",
        blank=True,
        related_name="thematic_feeds_blocked",
        verbose_name="Исключенные теги",
        help_text="Посты с этими тегами будут скрыты в папке.",
    )
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "feeds"
        ordering = ["sort_order", "name"]
        verbose_name = "Папка"
        verbose_name_plural = "Папки"

    def __str__(self) -> str:
        return self.name


__all__ = ["ThematicFeed"]

