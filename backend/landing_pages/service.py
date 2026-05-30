from __future__ import annotations

from django.conf import settings
from django.http import HttpRequest

from landing_pages.models import LandingPage, LandingPageImage


def absolute_url(request: HttpRequest, url: str) -> str:
    if not url:
        return ""
    if url.startswith(("http://", "https://")):
        return url
    site_base = (getattr(settings, "SITE_BASE_URL", "") or "").rstrip("/")
    return f"{site_base}{url}" if site_base else request.build_absolute_uri(url)


def serialize_image(request: HttpRequest, image: LandingPageImage) -> dict:
    image_url = image.effective_image_url
    return {
        "id": image.id,
        "slot": image.slot,
        "title": image.title,
        "alt_text": image.alt_text,
        "image_url": absolute_url(request, image_url) if image_url else "",
        "is_active": image.is_active,
        "sort_order": image.sort_order,
        "created_at": image.created_at.isoformat() if image.created_at else None,
        "updated_at": image.updated_at.isoformat() if image.updated_at else None,
    }


def serialize_page(request: HttpRequest, page: LandingPage, *, include_images: bool = True) -> dict:
    payload = {
        "id": page.id,
        "slug": page.slug,
        "title": page.title,
        "description": page.description,
        "template_slug": page.template_slug,
        "is_published": page.is_published,
        "sort_order": page.sort_order,
        "url": f"/l/{page.slug}",
        "created_at": page.created_at.isoformat() if page.created_at else None,
        "updated_at": page.updated_at.isoformat() if page.updated_at else None,
    }
    if include_images:
        images = getattr(page, "prefetched_images", None)
        if images is None:
            images = page.images.all()
        payload["images"] = [serialize_image(request, image) for image in images]
    return payload
