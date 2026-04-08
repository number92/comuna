from __future__ import annotations

from django.contrib.auth import get_user_model
from django.utils.text import slugify

from my_feed.models import ThematicFeed

User = get_user_model()


def _fv():
    from feeds import views as feeds_views

    return feeds_views


def _thematic_feed_is_moderator(user: User | None, feed: ThematicFeed) -> bool:
    if not user:
        return False
    if user.is_staff:
        return True
    return feed.moderators.filter(id=user.id).exists()


def _parse_int_list(value: object) -> list[int]:
    if not isinstance(value, list):
        return []
    result: list[int] = []
    seen: set[int] = set()
    for item in value:
        try:
            parsed = int(item)
        except (TypeError, ValueError):
            continue
        if parsed <= 0 or parsed in seen:
            continue
        seen.add(parsed)
        result.append(parsed)
    return result


def _normalize_thematic_feed_slug(value: str) -> str:
    normalized_value = str(value or "").strip()
    if not normalized_value:
        return ""
    base_slug = slugify(normalized_value)[:120]
    if not base_slug:
        base_slug = _fv()._slugify_title(normalized_value)[:120]
    return str(base_slug or "").strip("-")


def _can_access_thematic_folders_page(user: User | None) -> bool:
    if not user:
        return False
    if user.is_staff:
        return True
    return ThematicFeed.objects.filter(moderators=user).exists()


__all__ = [
    "_can_access_thematic_folders_page",
    "_normalize_thematic_feed_slug",
    "_parse_int_list",
    "_thematic_feed_is_moderator",
]
