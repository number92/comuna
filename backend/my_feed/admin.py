from django.contrib import admin

from my_feed.models import ThematicFeed


@admin.register(ThematicFeed)
class ThematicFeedAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "is_active",
        "sort_order",
        "moderators_count",
        "authors_count",
        "excluded_authors_count",
        "rubrics_count",
        "tags_count",
        "blocked_tags_count",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = (
        "moderators",
        "authors",
        "excluded_authors",
        "rubrics",
        "tags",
        "blocked_tags",
    )
    fields = (
        "name",
        "slug",
        "description",
        "moderators",
        "authors",
        "excluded_authors",
        "rubrics",
        "tags",
        "blocked_tags",
        "sort_order",
        "is_active",
    )

    def moderators_count(self, obj):
        return obj.moderators.count()

    moderators_count.short_description = "Модераторов"

    def authors_count(self, obj):
        return obj.authors.count()

    authors_count.short_description = "Авторов"

    def excluded_authors_count(self, obj):
        return obj.excluded_authors.count()

    excluded_authors_count.short_description = "Исключено авторов"

    def rubrics_count(self, obj):
        return obj.rubrics.count()

    rubrics_count.short_description = "Рубрик"

    def tags_count(self, obj):
        return obj.tags.count()

    tags_count.short_description = "Тегов"

    def blocked_tags_count(self, obj):
        return obj.blocked_tags.count()

    blocked_tags_count.short_description = "Исключено тегов"

