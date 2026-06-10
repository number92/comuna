# Миграции `legacy_migration`

Пошаговый перенос на prod: **[PROD_RUNBOOK.md](PROD_RUNBOOK.md)**.

## Map-таблицы (Postgres)

- **`0002_wp_legacy_maps.py`** — только `LegacyWpUserMap`, `LegacyWpPostMap`, `LegacyWpCommentMap`.
- **`0001_wp_legacy_maps.py`** — зеркало WP (`managed=False`), таблицы в Postgres **не создаёт**.

## Команды

```bash
python manage.py migrate legacy_migration
```

Если таблицы `legacy_migration_legacywp*` уже есть после старого `0001` (всё в одном файле):

```bash
python manage.py migrate legacy_migration 0002_wp_legacy_maps --fake
```

## `makemigrations`

```bash
python manage.py makemigrations legacy_migration
```

**Не запускайте** `makemigrations feeds` на ветке legacy: при отставании от `main` Django может снова сгенерировать дубликат `0118` как `0100_rename_*` и сломать граф. Для `feeds` используйте только миграции из `main`.

Если на dev уже применили ошибочную `feeds.0100_rename_*` (её нет на проде):

```sql
DELETE FROM django_migrations
WHERE app = 'feeds'
  AND name = '0100_rename_feeds_mobile_user_id_680b49_idx_feeds_mobil_user_id_6bb55c_idx_and_more';
```

Затем `python manage.py migrate`. Если индексы уже переименованы, при падении на `0118` — `migrate feeds 0118 --fake`.

Map-модели: `legacy_migration/models/mapping.py`. Зеркало WP: `models/wp_mirror.py`.  
Если изменений нет — будет `No changes detected` (это нормально).
