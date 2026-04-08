from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class AuthorAdmin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author_links")
    author = models.ForeignKey("feeds.Author", on_delete=models.CASCADE, related_name="admin_links")
    telegram_user_id = models.BigIntegerField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "feeds"
        unique_together = ("user", "author")

    def __str__(self) -> str:
        return f"{self.user_id}:{self.author_id}"


class AuthorVerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author_codes")
    code = models.CharField(max_length=64, unique=True)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "feeds"

    def __str__(self) -> str:
        return f"{self.user_id}:{self.code}"


from telegram_integration.models import TelegramAccount


class VkAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="vk_account")
    vk_id = models.BigIntegerField(unique=True)
    username = models.CharField(blank=True, max_length=255)
    first_name = models.CharField(blank=True, max_length=255)
    last_name = models.CharField(blank=True, max_length=255)
    avatar_url = models.URLField(blank=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "feeds"

    def __str__(self) -> str:
        return f"vk:{self.vk_id}"


class SiteUserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="site_profile")
    display_name = models.CharField(max_length=120, blank=True)
    avatar_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "feeds"
        verbose_name = "Профиль пользователя сайта"
        verbose_name_plural = "Профили пользователей сайта"

    def __str__(self) -> str:
        return f"site-profile:{self.user_id}"


__all__ = [
    "AuthorAdmin",
    "AuthorVerificationCode",
    "SiteUserProfile",
    "TelegramAccount",
    "VkAccount",
]
