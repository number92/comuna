from django.contrib import admin

from notifications.models import SiteNotification, SiteNotificationPreference


@admin.register(SiteNotificationPreference)
class SiteNotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "event_key", "site_enabled", "telegram_enabled", "updated_at")
    list_filter = ("event_key", "site_enabled", "telegram_enabled")
    search_fields = ("user__username", "event_key")
    raw_id_fields = ("user",)


@admin.register(SiteNotification)
class SiteNotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "event_key",
        "title",
        "is_site",
        "is_telegram",
        "read_at",
        "telegram_sent_at",
        "created_at",
    )
    list_filter = ("event_key", "is_site", "is_telegram")
    search_fields = ("user__username", "title", "message", "event_key")
    raw_id_fields = ("user",)

