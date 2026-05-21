from __future__ import annotations

import hmac
import json
import os
import re
import secrets
import urllib.error
import urllib.parse
import urllib.request
from html import escape
from typing import Any

from django.conf import settings
from django.db import IntegrityError, transaction
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from communities import service as community_service
from communities.models import Comun, ComunCategory, ComunPostCategoryAssignment
from feeds.models import Author, Post
from rabotaem_backend.images import save_image_with_variants
from telegram_integration.media import build_public_storage_url, safe_public_url

WHEREFILMED_COMUN_SLUG = "wherefilmed"
WHEREFILMED_CATEGORY_NAME = "локации"
WHEREFILMED_AUTHOR_USERNAME = "wherefilmed"
WHEREFILMED_MESSAGE_ID_BASE = -3_000_000_000_000
WHEREFILMED_IMAGE_MAX_BYTES = 15 * 1024 * 1024


class WhereFilmedImportError(Exception):
    def __init__(self, message: str, status: int = 400) -> None:
        super().__init__(message)
        self.status = status


def _site_url(path: str) -> str:
    base_url = str(getattr(settings, "SITE_BASE_URL", "") or "").strip().rstrip("/")
    clean_path = f"/{str(path or '').lstrip('/')}"
    return f"{base_url}{clean_path}" if base_url else clean_path


def _post_public_url(post: Post) -> str:
    post_title = str(post.title or "").strip() or f"post-{post.id}"
    post_slug = community_service._slugify_title(post_title)
    return _site_url(f"/b/post/{post.id}-{post_slug}" if post_slug else f"/b/post/{post.id}")


def _auth_token() -> str:
    return (
        str(getattr(settings, "WHEREFILMED_IMPORT_TOKEN", "") or "").strip()
        or str(getattr(settings, "TAMBUR_EXPORT_TOKEN", "") or "").strip()
    )


def _check_auth(request: HttpRequest) -> None:
    expected = _auth_token()
    if not expected:
        raise WhereFilmedImportError("wherefilmed import token is not configured", 503)

    authorization = str(request.headers.get("Authorization") or "").strip()
    prefix = "Bearer "
    supplied = authorization[len(prefix) :].strip() if authorization.startswith(prefix) else ""
    if not supplied or not hmac.compare_digest(supplied, expected):
        raise WhereFilmedImportError("unauthorized", 401)


def _as_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        parsed = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _source_key(payload: dict[str, Any]) -> tuple[str, int]:
    source = payload.get("source")
    if not isinstance(source, dict):
        raise WhereFilmedImportError("source is required")

    site = re.sub(r"\s+", "", str(source.get("site") or "").strip().lower())
    movie_id = _as_int(source.get("movie_id"))
    if site != "wherefilmed" or not movie_id:
        raise WhereFilmedImportError("source.site and source.movie_id are invalid")
    return site, movie_id


def _wherefilmed_message_id(movie_id: int) -> int:
    return WHEREFILMED_MESSAGE_ID_BASE - int(movie_id)


def _wherefilmed_author() -> Author:
    author, _created = Author.objects.get_or_create(
        username=WHEREFILMED_AUTHOR_USERNAME,
        defaults={
            "title": "WhereFilmed",
            "channel_url": "https://wherefilmed.org",
            "invite_url": "https://wherefilmed.org",
            "description": "Материалы WhereFilmed о местах съемок фильмов и сериалов.",
            "auto_publish": True,
        },
    )
    updates: list[str] = []
    if author.title != "WhereFilmed":
        author.title = "WhereFilmed"
        updates.append("title")
    if not author.channel_url:
        author.channel_url = "https://wherefilmed.org"
        updates.append("channel_url")
    if not author.invite_url:
        author.invite_url = "https://wherefilmed.org"
        updates.append("invite_url")
    if updates:
        author.save(update_fields=[*updates, "updated_at"])
    return author


def _target_comun_and_category() -> tuple[Comun, ComunCategory]:
    comun = Comun.objects.filter(slug=WHEREFILMED_COMUN_SLUG, is_active=True).first()
    if not comun:
        raise WhereFilmedImportError("wherefilmed community is not configured", 500)

    category, _created = community_service._ensure_comun_category_by_name(
        comun,
        WHEREFILMED_CATEGORY_NAME,
    )
    if not category:
        raise WhereFilmedImportError("wherefilmed category is not configured", 500)
    return comun, category


def _public_url(value: object) -> str:
    raw = safe_public_url(str(value or "").strip())
    if not raw:
        return ""
    if raw.startswith("//"):
        raw = f"https:{raw}"
    parsed = urllib.parse.urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    return urllib.parse.urlunparse(parsed._replace(fragment=""))


def _download_image(url: str, *, movie_id: int) -> str:
    source_url = _public_url(url)
    if not source_url:
        return ""

    max_bytes = int(getattr(settings, "WHEREFILMED_IMPORT_IMAGE_MAX_BYTES", WHEREFILMED_IMAGE_MAX_BYTES))
    request = urllib.request.Request(
        source_url,
        headers={
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "User-Agent": "TamburWhereFilmedImporter/1.0 (+https://tambur.pub)",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            data = response.read(max_bytes + 1)
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise WhereFilmedImportError(f"failed to download image: {source_url}", 502) from exc

    if len(data) > max_bytes:
        raise WhereFilmedImportError(f"image is too large: {source_url}", 413)
    if not data:
        raise WhereFilmedImportError(f"image is empty: {source_url}", 502)

    parsed = urllib.parse.urlparse(source_url)
    ext = os.path.splitext(parsed.path)[1].lower()
    if not ext or len(ext) > 8:
        ext = ".jpg"
    filename = f"posts/wherefilmed/{movie_id}/{secrets.token_hex(10)}{ext}"
    image_set = save_image_with_variants(data=data, original_path=filename)
    return build_public_storage_url(image_set.default_url)


def _gallery_items(raw_items: object, *, movie_id: int) -> list[dict[str, str]]:
    if not isinstance(raw_items, list):
        return []

    result: list[dict[str, str]] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        source_url = item.get("image_url") or item.get("url") or item.get("thumbnail_url")
        local_url = _download_image(str(source_url or ""), movie_id=movie_id)
        if local_url:
            result.append({"url": local_url, "alt": "", "title": ""})
    return result


def _text(value: object, max_length: int | None = None) -> str:
    normalized = re.sub(r"\s+", " ", str(value or "").strip())
    return normalized[:max_length] if max_length else normalized


def _list_titles(items: object) -> list[str]:
    if not isinstance(items, list):
        return []
    titles: list[str] = []
    seen: set[str] = set()
    for item in items:
        title = _text(item.get("title") if isinstance(item, dict) else item)
        key = title.lower()
        if title and key not in seen:
            seen.add(key)
            titles.append(title)
    return titles


def _movie_title(movie: dict[str, Any]) -> str:
    title = _text(movie.get("title"), 180)
    original_title = _text(movie.get("original_title"), 180)
    year = _as_int(movie.get("year"))
    if original_title and original_title.lower() != title.lower():
        title = f"{title} / {original_title}" if title else original_title
    if year:
        title = f"{title} ({year})" if title else str(year)
    return title or "WhereFilmed"


def _post_title(movie: dict[str, Any]) -> str:
    return f"Где снимали «{_movie_title(movie)}»"[:255]


def _editor_paragraph_html(value: str) -> str:
    html = str(value or "").strip()
    if not html:
        return ""
    html = re.sub(r"</p>\s*<p\b[^>]*>", "<br><br>", html, flags=re.IGNORECASE)
    html = re.sub(r"^\s*<p\b[^>]*>", "", html, flags=re.IGNORECASE)
    html = re.sub(r"</p>\s*$", "", html, flags=re.IGNORECASE)
    return html.strip()


def _paragraph_block(text: str, block_id: str) -> dict[str, Any] | None:
    value = _editor_paragraph_html(text)
    if not value:
        return None
    return {"id": block_id, "type": "paragraph", "data": {"text": value}}


def _header_block(text: str, block_id: str, level: int = 2) -> dict[str, Any] | None:
    value = _text(text)
    if not value:
        return None
    return {"id": block_id, "type": "header", "data": {"text": escape(value), "level": level}}


def _gallery_block(images: list[dict[str, str]], block_id: str) -> dict[str, Any] | None:
    if not images:
        return None
    return {"id": block_id, "type": "gallery", "data": {"images": images}}


def _image_block(url: str, caption: str, block_id: str) -> dict[str, Any] | None:
    if not url:
        return None
    return {
        "id": block_id,
        "type": "image",
        "data": {
            "file": {"url": url, "alt": caption, "title": caption},
            "caption": escape(caption),
        },
    }


def _location_meta_html(location: dict[str, Any]) -> str:
    parts: list[str] = []
    cities = ", ".join(_list_titles(location.get("cities")))
    places = ", ".join(_list_titles(location.get("places")))
    address = _text(location.get("address"))
    timing = _text(location.get("timing"))
    season = _as_int(location.get("season"))
    episode = _as_int(location.get("episode"))
    gps = _text(location.get("gps_coordinate"))
    map_link = _public_url(location.get("map_link"))

    if cities:
        parts.append(f"<b>Город:</b> {escape(cities)}")
    if places:
        parts.append(f"<b>Место:</b> {escape(places)}")
    if address:
        parts.append(f"<b>Адрес:</b> {escape(address)}")
    if timing:
        parts.append(f"<b>Тайминг:</b> {escape(timing)}")
    if season and episode:
        parts.append(f"<b>Эпизод:</b> S{season:02d}E{episode:02d}")
    elif episode:
        parts.append(f"<b>Эпизод:</b> {episode}")
    if gps:
        parts.append(f"<b>Координаты:</b> {escape(gps)}")
    if map_link:
        parts.append(f'<a href="{escape(map_link, quote=True)}" target="_blank" rel="noopener noreferrer">Открыть карту</a>')
    return "<br>".join(parts)


def _build_content(
    payload: dict[str, Any],
    *,
    movie_id: int,
) -> tuple[str, list[str], dict[str, Any]]:
    movie = payload.get("movie") if isinstance(payload.get("movie"), dict) else {}
    locations = payload.get("locations") if isinstance(payload.get("locations"), list) else []

    blocks: list[dict[str, Any]] = []
    saved_images: list[str] = []

    poster_url = _download_image(str(movie.get("poster_url") or ""), movie_id=movie_id)
    if poster_url:
        saved_images.append(poster_url)
        block = _image_block(poster_url, _movie_title(movie), "wf-poster")
        if block:
            blocks.append(block)

    description_html = str(movie.get("description_html") or "").strip()
    description_text = _text(movie.get("description_text"))
    description_block = _paragraph_block(description_html or escape(description_text), "wf-description")
    if description_block:
        blocks.append(description_block)

    movie_meta: list[str] = []
    countries = ", ".join(_list_titles(movie.get("countries")))
    genres = ", ".join(_list_titles(movie.get("genres")))
    source = payload.get("source") if isinstance(payload.get("source"), dict) else {}
    source_url = _public_url(source.get("url"))
    trailer_url = _public_url(movie.get("trailer_url"))
    if countries:
        movie_meta.append(f"<b>Страны:</b> {escape(countries)}")
    if genres:
        movie_meta.append(f"<b>Жанры:</b> {escape(genres)}")
    if trailer_url:
        movie_meta.append(f'<a href="{escape(trailer_url, quote=True)}" target="_blank" rel="noopener noreferrer">Трейлер</a>')
    if source_url:
        movie_meta.append(f'<a href="{escape(source_url, quote=True)}" target="_blank" rel="noopener noreferrer">Оригинальная карточка WhereFilmed</a>')
    meta_block = _paragraph_block("<br>".join(movie_meta), "wf-movie-meta")
    if meta_block:
        blocks.append(meta_block)

    if locations:
        header = _header_block("Локации съемок", "wf-locations", level=2)
        if header:
            blocks.append(header)

    source_locations: list[dict[str, Any]] = []
    for index, raw_location in enumerate(locations, start=1):
        if not isinstance(raw_location, dict):
            continue
        location_id = _as_int(raw_location.get("id")) or index
        location_title = _text(raw_location.get("title")) or f"Локация {index}"

        header = _header_block(location_title, f"wf-location-{location_id}", level=3)
        if header:
            blocks.append(header)

        meta_html = _location_meta_html(raw_location)
        meta = _paragraph_block(meta_html, f"wf-location-{location_id}-meta")
        if meta:
            blocks.append(meta)

        scene_html = str(raw_location.get("scene_description_html") or "").strip()
        if not scene_html:
            scene_html = escape(_text(raw_location.get("scene_description_text")))
        scene = _paragraph_block(scene_html, f"wf-location-{location_id}-scene")
        if scene:
            blocks.append(scene)

        spot_html = str(raw_location.get("movie_spot_html") or "").strip()
        if not spot_html:
            spot_html = escape(_text(raw_location.get("movie_spot_text")))
        spot = _paragraph_block(spot_html, f"wf-location-{location_id}-spot")
        if spot:
            blocks.append(spot)

        movie_gallery = _gallery_items(raw_location.get("movie_gallery"), movie_id=movie_id)
        reality_gallery = _gallery_items(raw_location.get("reality_gallery"), movie_id=movie_id)
        saved_images.extend(item["url"] for item in [*movie_gallery, *reality_gallery])

        gallery = _gallery_block(movie_gallery, f"wf-location-{location_id}-movie-gallery")
        if gallery:
            blocks.append(gallery)
        reality = _gallery_block(reality_gallery, f"wf-location-{location_id}-reality-gallery")
        if reality:
            blocks.append(reality)

        source_locations.append(
            {
                "id": raw_location.get("id"),
                "title": location_title,
                "movie_gallery_count": len(movie_gallery),
                "reality_gallery_count": len(reality_gallery),
            }
        )

    content = json.dumps({"time": 0, "blocks": blocks, "version": "2.31.0"}, ensure_ascii=False)
    image_payload = {"poster_url": poster_url, "saved_image_urls": saved_images, "locations": source_locations}
    return content, saved_images, image_payload


def _raw_data(
    payload: dict[str, Any],
    *,
    movie_id: int,
    saved_images: list[str],
    image_payload: dict[str, Any],
) -> dict[str, Any]:
    source = payload.get("source") if isinstance(payload.get("source"), dict) else {}
    source_url = _public_url(source.get("url"))
    return {
        "source": "manual_comun",
        "comun_slug": WHEREFILMED_COMUN_SLUG,
        "comun_category_name": WHEREFILMED_CATEGORY_NAME,
        "wherefilmed": {
            "source_site": "wherefilmed",
            "movie_id": movie_id,
            "slug": source.get("slug"),
            "url": source.get("url"),
            "payload_version": payload.get("payload_version"),
            "images": image_payload,
        },
        "gallery_urls": saved_images[:20],
    }


def _import_payload(payload: dict[str, Any]) -> tuple[Post, bool]:
    if payload.get("payload_version") != 1:
        raise WhereFilmedImportError("unsupported payload_version")

    _site, movie_id = _source_key(payload)
    author = _wherefilmed_author()
    message_id = _wherefilmed_message_id(movie_id)

    existing = Post.objects.filter(author=author, message_id=message_id).first()
    comun, category = _target_comun_and_category()
    if existing:
        ComunPostCategoryAssignment.objects.update_or_create(
            comun=comun,
            post=existing,
            defaults={"category": category, "assigned_by": None},
        )
        return existing, False

    movie = payload.get("movie") if isinstance(payload.get("movie"), dict) else {}
    content, saved_images, image_payload = _build_content(payload, movie_id=movie_id)
    raw_data = _raw_data(payload, movie_id=movie_id, saved_images=saved_images, image_payload=image_payload)
    source = payload.get("source") if isinstance(payload.get("source"), dict) else {}

    try:
        with transaction.atomic():
            post, created = Post.objects.get_or_create(
                author=author,
                message_id=message_id,
                defaults={
                    "title": _post_title(movie),
                    "content": content,
                    "source_url": source_url[:255],
                    "channel_url": author.channel_url,
                    "raw_data": raw_data,
                    "is_pending": False,
                    "is_blocked": False,
                    "publish_at": None,
                },
            )
            ComunPostCategoryAssignment.objects.update_or_create(
                comun=comun,
                post=post,
                defaults={"category": category, "assigned_by": None},
            )
    except IntegrityError:
        post = Post.objects.get(author=author, message_id=message_id)
        created = False

    community_service._recalculate_comun_rating(comun.id)
    return post, created


@csrf_exempt
def wherefilmed_import(request: HttpRequest) -> HttpResponse:
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "method not allowed"}, status=405)

    try:
        _check_auth(request)
        payload = json.loads(request.body.decode("utf-8") or "{}")
        if not isinstance(payload, dict):
            raise WhereFilmedImportError("invalid json payload")
        post, created = _import_payload(payload)
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "invalid json"}, status=400)
    except WhereFilmedImportError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=exc.status)

    status = 201 if created else 200
    return JsonResponse({"id": str(post.id), "url": _post_public_url(post)}, status=status)


__all__ = [
    "wherefilmed_import",
]
