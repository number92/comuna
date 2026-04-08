from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class SiteNotificationPreference(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notification_preferences"
    )
    event_key = models.CharField(max_length=80)
    site_enabled = models.BooleanField(default=True)
    telegram_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "feeds"
        verbose_name = "Настройка уведомления"
        verbose_name_plural = "Настройки уведомлений"
        unique_together = ("user", "event_key")
        indexes = [
            models.Index(fields=("user", "event_key")),
        ]

    def __str__(self) -> str:
        return f"notification-pref:{self.user_id}:{self.event_key}"


class SiteNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="site_notifications")
    event_key = models.CharField(max_length=80)
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    link_url = models.CharField(max_length=500, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    is_site = models.BooleanField(default=True)
    is_telegram = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    telegram_sent_at = models.DateTimeField(null=True, blank=True)
    telegram_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "feeds"
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ("-created_at", "-id")
        indexes = [
            models.Index(fields=("user", "created_at")),
            models.Index(fields=("user", "read_at")),
            models.Index(fields=("user", "is_site")),
        ]

    def __str__(self) -> str:
        return f"notification:{self.user_id}:{self.event_key}:{self.id}"


__all__ = [
    "SiteNotification",
    "SiteNotificationPreference",
]

