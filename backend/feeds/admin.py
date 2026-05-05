from django import forms
from django.contrib import admin

from editor.models import post_template_type_choices

from .models import (
    Author,
    Post,
    PostComment,
    PostCommentLike,
    PostLike,
    Rubric,
    StaticPageContent,
    Tag,
    TagRelation,
    TagRelationType,
    normalize_allowed_post_templates,
)


class RubricAdminForm(forms.ModelForm):
    allowed_post_templates = forms.MultipleChoiceField(
        label="Доступные шаблоны поста",
        choices=(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Разрешенные шаблоны для публикации в рубрике.",
    )

    class Meta:
        model = Rubric
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["allowed_post_templates"].choices = post_template_type_choices()
        self.fields["allowed_post_templates"].initial = normalize_allowed_post_templates(
            getattr(self.instance, "allowed_post_templates", None)
        )

    def clean_allowed_post_templates(self):
        return normalize_allowed_post_templates(self.cleaned_data.get("allowed_post_templates"))


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "title",
        "rubric",
        "auto_publish",
        "publish_delay_days",
        "notify_comments",
        "rating_total",
        "shadow_banned",
        "force_home",
        "is_blocked",
        "created_at",
    )
    list_filter = (
        "rubric",
        "auto_publish",
        "notify_comments",
        "shadow_banned",
        "force_home",
        "is_blocked",
    )
    search_fields = ("username", "title")



@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "rubric",
        "message_id",
        "is_pending",
        "is_blocked",
        "publish_at",
        "created_at",
    )
    list_filter = ("is_pending", "is_blocked", "author", "rubric")
    search_fields = ("title", "content", "author__username")
    raw_id_fields = ("author", "rubric")
    fields = (
        "author",
        "rubric",
        "tags",
        "message_id",
        "title",
        "content",
        "rating",
        "comments_count",
        "source_url",
        "channel_url",
        "is_pending",
        "is_blocked",
        "publish_at",
        "raw_data",
    )
    filter_horizontal = ("tags",)


class TagRelationInline(admin.TabularInline):
    model = TagRelation
    fk_name = "from_tag"
    extra = 1
    autocomplete_fields = ("to_tag", "relation_type")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "mood", "lemma", "is_active", "hide_from_home")
    list_filter = ("mood", "is_active", "hide_from_home")
    search_fields = ("name", "lemma")
    inlines = (TagRelationInline,)


@admin.register(TagRelation)
class TagRelationAdmin(admin.ModelAdmin):
    list_display = ("from_tag", "to_tag", "relation_type", "created_at")
    list_filter = ("relation_type",)
    search_fields = ("from_tag__name", "to_tag__name")
    raw_id_fields = ("from_tag", "to_tag")


@admin.register(TagRelationType)
class TagRelationTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "is_bidirectional", "created_at")
    search_fields = ("name",)


@admin.register(Rubric)
class RubricAdmin(admin.ModelAdmin):
    form = RubricAdminForm
    list_display = (
        "name",
        "slug",
        "hide_from_home",
        "allow_for_telegram_channel",
        "is_active",
        "is_hidden",
        "sort_order",
    )
    list_filter = ("hide_from_home", "allow_for_telegram_channel", "is_active", "is_hidden")
    search_fields = ("name", "slug")
    fields = (
        "name",
        "slug",
        "description",
        "icon_url",
        "cover_image_url",
        "subscribe_url",
        "home_limit",
        "hide_from_home",
        "allow_for_telegram_channel",
        "allowed_post_templates",
        "sort_order",
        "is_active",
        "is_hidden",
    )


@admin.register(StaticPageContent)
class StaticPageContentAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "updated_by", "updated_at")
    search_fields = ("slug", "title")
    readonly_fields = ("created_at", "updated_at")
    fields = ("slug", "title", "content", "updated_by", "created_at", "updated_at")


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "persona_username", "parent", "created_at", "is_deleted")
    list_filter = ("is_deleted",)
    search_fields = ("body", "user__username", "persona_username", "post__title")
    raw_id_fields = ("post", "user", "parent")


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "value", "created_at")
    search_fields = ("user__username", "post__title")
    raw_id_fields = ("post", "user")


@admin.register(PostCommentLike)
class PostCommentLikeAdmin(admin.ModelAdmin):
    list_display = ("comment", "user", "created_at")
    search_fields = ("user__username", "comment__post__title")
    raw_id_fields = ("comment", "user")
