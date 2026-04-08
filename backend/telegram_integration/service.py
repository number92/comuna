from __future__ import annotations

import hashlib
import hmac
import json
import re
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from notifications.models import SiteNotification
from telegram_integration.models import TelegramAccount

User = get_user_model()

_TELEGRAM_LOGIN_FIELDS = {
    "id",
    "first_name",
    "last_name",
    "username",
    "photo_url",
    "auth_date",
}


def verify_telegram_login(payload: dict) -> tuple[bool, str | None]:
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        return False, "telegram auth disabled"
    provided_hash = payload.get("hash")
    if not provided_hash:
        return False, "missing hash"
    data = {
        k: v
        for k, v in payload.items()
        if k in _TELEGRAM_LOGIN_FIELDS and v is not None
    }
    auth_date_raw = data.get("auth_date")
    try:
        auth_date = int(auth_date_raw)
    except (TypeError, ValueError):
        return False, "invalid auth date"
    now_ts = int(timezone.now().timestamp())
    if now_ts - auth_date > 60 * 60 * 24:
        return False, "auth expired"
    for key, value in list(data.items()):
        data[key] = str(value)
    data_check_string = "\n".join(f"{key}={data[key]}" for key in sorted(data.keys()))
    secret_key = hashlib.sha256(token.encode("utf-8")).digest()
    computed_hash = hmac.new(
        secret_key, data_check_string.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    if computed_hash != provided_hash:
        return False, "invalid hash"
    return True, None


def generate_unique_username(base: str, suffix: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9_]", "_", base).strip("_")
    if not base:
        base = "user"
    candidate = base
    if User.objects.filter(username__iexact=candidate).exists():
        candidate = f"{base}_{suffix}"
    if User.objects.filter(username__iexact=candidate).exists():
        candidate = f"tg_{suffix}"
    return candidate[:150]


def validate_telegram_login(payload: dict) -> None:
    ok, error_message = verify_telegram_login(payload)
    if not ok:
        raise ValueError(error_message or "invalid telegram auth")


def upsert_telegram_account(payload: dict):
    try:
        telegram_id = int(payload.get("id"))
    except (TypeError, ValueError):
        raise ValueError("invalid telegram id") from None

    username = (payload.get("username") or "").strip()
    first_name = (payload.get("first_name") or "").strip()
    last_name = (payload.get("last_name") or "").strip()
    avatar_url = (payload.get("photo_url") or "").strip()

    account = TelegramAccount.objects.select_related("user").filter(telegram_id=telegram_id).first()
    if account:
        user = account.user
    else:
        base_username = username or (first_name or "tg")
        candidate = generate_unique_username(base_username, str(telegram_id))
        user = User.objects.create_user(username=candidate)
        user.set_unusable_password()
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        user.save(update_fields=["password", "first_name", "last_name"])
        account = TelegramAccount.objects.create(
            user=user,
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            avatar_url=avatar_url,
        )

    account.username = username
    account.first_name = first_name
    account.last_name = last_name
    account.avatar_url = avatar_url
    account.save(update_fields=["username", "first_name", "last_name", "avatar_url", "updated_at"])
    return user


def build_telegram_login_redirect_html(token: str, next_url: str) -> str:
    next_literal = json.dumps(next_url or "/")
    return (
        "<!doctype html><html><head><meta charset=\"utf-8\">"
        "<title>Telegram login</title></head><body>"
        "<script>"
        f"try{{localStorage.setItem('comuna.site.token','{token}');}}catch(e){{}}"
        f"window.location.replace({next_literal});"
        "</script>"
        "</body></html>"
    )


def notification_link_absolute(link_url: str) -> str:
    value = (link_url or "").strip()
    if not value:
        return ""
    if value.startswith("http://") or value.startswith("https://"):
        return value
    base = (getattr(settings, "SITE_BASE_URL", "") or "").rstrip("/")
    if not base:
        return value
    if not value.startswith("/"):
        value = f"/{value}"
    return f"{base}{value}"


def send_site_notification_to_telegram(notification: SiteNotification) -> None:
    if not notification.is_telegram:
        return
    token = (getattr(settings, "TELEGRAM_BOT_TOKEN", "") or "").strip()
    if not token:
        return

    account = TelegramAccount.objects.filter(user=notification.user).first()
    if not account:
        return

    parts = [notification.title.strip()]
    if notification.message.strip():
        parts.append(notification.message.strip())
    link = notification_link_absolute(notification.link_url)
    if link:
        parts.append(link)
    text = "\n\n".join([part for part in parts if part]).strip()
    if not text:
        return

    payload = urllib.parse.urlencode(
        {"chat_id": str(account.telegram_id), "text": text[:4096]}
    ).encode("utf-8")
    if not payload:
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        request = urllib.request.Request(url, data=payload, method="POST")
        with urllib.request.urlopen(request, timeout=5) as response:
            json.loads(response.read().decode("utf-8") or "{}")
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        notification.telegram_error = str(exc)
        notification.save(update_fields=["telegram_error", "updated_at"])
        return
    except Exception as exc:
        notification.telegram_error = str(exc)
        notification.save(update_fields=["telegram_error", "updated_at"])
        return

    notification.telegram_sent_at = timezone.now()
    notification.telegram_error = ""
    notification.save(update_fields=["telegram_sent_at", "telegram_error", "updated_at"])


__all__ = [
    "build_telegram_login_redirect_html",
    "generate_unique_username",
    "notification_link_absolute",
    "send_site_notification_to_telegram",
    "upsert_telegram_account",
    "validate_telegram_login",
    "verify_telegram_login",
]
