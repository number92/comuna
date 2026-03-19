from django.db import migrations, models


def backfill_rubrics_to_comuns(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Rubric = apps.get_model("feeds", "Rubric")
    Comun = apps.get_model("feeds", "Comun")

    db_alias = schema_editor.connection.alias
    creator = User.objects.using(db_alias).filter(id=1).first()
    if creator is None:
        raise RuntimeError("User with id=1 not found; cannot backfill rubric communities")

    moderators_through = Comun.moderators.through

    for rubric in Rubric.objects.using(db_alias).filter(is_active=True).order_by("sort_order", "name", "id"):
        comun = (
            Comun.objects.using(db_alias)
            .filter(source_rubric_id=rubric.id)
            .order_by("id")
            .first()
        )
        if comun is None:
            comun = (
                Comun.objects.using(db_alias)
                .filter(slug__iexact=rubric.slug)
                .order_by("id")
                .first()
            )
        if comun is None:
            comun = (
                Comun.objects.using(db_alias)
                .filter(name__iexact=rubric.name)
                .order_by("id")
                .first()
            )

        if comun is None:
            comun = Comun.objects.using(db_alias).create(
                name=(rubric.name or "")[:160],
                slug=(rubric.slug or "")[:160],
                creator_id=creator.id,
                source_rubric_id=rubric.id,
                website_url=(rubric.subscribe_url or "")[:500],
                product_description=rubric.description or "",
                hide_from_home=bool(rubric.hide_from_home),
                allowed_post_templates=rubric.allowed_post_templates,
                is_active=bool(rubric.is_active),
                sort_order=int(rubric.sort_order or 0),
            )
        else:
            updated_fields = []
            if comun.creator_id != creator.id:
                comun.creator_id = creator.id
                updated_fields.append("creator")
            if comun.source_rubric_id != rubric.id:
                comun.source_rubric_id = rubric.id
                updated_fields.append("source_rubric")
            if not comun.product_description and rubric.description:
                comun.product_description = rubric.description
                updated_fields.append("product_description")
            if not comun.website_url and rubric.subscribe_url:
                comun.website_url = (rubric.subscribe_url or "")[:500]
                updated_fields.append("website_url")
            if not comun.hide_from_home and rubric.hide_from_home:
                comun.hide_from_home = True
                updated_fields.append("hide_from_home")
            if (not comun.allowed_post_templates) and rubric.allowed_post_templates:
                comun.allowed_post_templates = rubric.allowed_post_templates
                updated_fields.append("allowed_post_templates")
            if (not comun.sort_order) and rubric.sort_order:
                comun.sort_order = int(rubric.sort_order or 0)
                updated_fields.append("sort_order")
            if updated_fields:
                comun.save(update_fields=updated_fields)

        moderators_through.objects.using(db_alias).get_or_create(
            comun_id=comun.id,
            user_id=creator.id,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("feeds", "0077_comun_only_moderators_can_post"),
    ]

    operations = [
        migrations.AddField(
            model_name="comun",
            name="source_rubric",
            field=models.OneToOneField(
                blank=True,
                help_text="Если указана, посты этой рубрики отображаются в сообществе.",
                null=True,
                on_delete=models.SET_NULL,
                related_name="source_comun",
                to="feeds.rubric",
                verbose_name="Исходная рубрика",
            ),
        ),
        migrations.RunPython(backfill_rubrics_to_comuns, migrations.RunPython.noop),
    ]
