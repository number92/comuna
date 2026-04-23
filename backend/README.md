# Django backend

## Quick start (local)

1. Create a virtualenv and install deps:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

2. Set env vars:

```bash
export DJANGO_SECRET_KEY=dev-secret
export DJANGO_DEBUG=1
export POSTGRES_DB=rabotaem
export POSTGRES_USER=rabotaem
export POSTGRES_PASSWORD=rabotaem
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export TELEGRAM_BOT_TOKEN=your-token
export TELEGRAM_WEBHOOK_SECRET=your-secret
export TELEGRAM_USE_POLLING=0
export PUSH_FCM_PROJECT_ID=your-firebase-project-id
export PUSH_FCM_SERVICE_ACCOUNT_FILE=/absolute/path/firebase-service-account.json
```

3. Migrate and run:

```bash
python backend/manage.py migrate
python backend/manage.py createsuperuser
python backend/manage.py runserver 0.0.0.0:8000
```

## Telegram webhook

1. Create a bot with BotFather and add it as an admin in the channel.
2. Set webhook (replace domain and secret):

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -d "url=https://your-domain.com/tg/webhook/<YOUR_SECRET>/" \
  -d "secret_token=<YOUR_SECRET>"
```

The backend accepts only channel posts and ignores other update types.

## Telegram polling (IPv6-only)

If webhook is not available, enable polling:

```bash
export TELEGRAM_USE_POLLING=1
```

Polling will disable webhook on startup and consume updates via `getUpdates`.

To import history, forward channel posts to the bot in a private chat.

## API

- `GET /api/authors/<username>/posts/?limit=20`
- `GET|POST|PATCH|DELETE /api/auth/notifications/push-devices/`

Returns the latest posts for a channel/author. Blocked authors or posts are hidden.

`/api/auth/notifications/push-devices/` allows the mobile app to register or deactivate
FCM device tokens for Android and iOS. The authenticated user is taken from the Bearer token.

## Admin

- `GET /admin/`

Use admin to block authors or individual posts.
