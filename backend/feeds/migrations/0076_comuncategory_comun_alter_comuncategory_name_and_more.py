import django.db.models.deletion
from django.db import migrations, models


def _resolve_through_field_names(through_model):
    comun_field_name = None
    category_field_name = None
    for field in through_model._meta.fields:
        remote_model = getattr(getattr(field, "remote_field", None), "model", None)
        model_name = getattr(getattr(remote_model, "_meta", None), "model_name", "")
        if model_name == "comun":
            comun_field_name = field.name
        elif model_name == "comuncategory":
            category_field_name = field.name
    if not comun_field_name or not category_field_name:
        raise RuntimeError("Unable to resolve ComunCategory through fields")
    return comun_field_name, category_field_name


def forwards(apps, schema_editor):
    Comun = apps.get_model("feeds", "Comun")
    ComunCategory = apps.get_model("feeds", "ComunCategory")
    ComunPostCategoryAssignment = apps.get_model("feeds", "ComunPostCategoryAssignment")
    through_model = Comun.categories.through
    comun_field_name, category_field_name = _resolve_through_field_names(through_model)

    for category in ComunCategory.objects.all().order_by("id"):
        through_rows = list(
            through_model.objects.filter(**{category_field_name: category.id})
            .order_by("id")
            .values("id", comun_field_name)
        )
        assignment_comun_ids = list(
            ComunPostCategoryAssignment.objects.filter(category_id=category.id)
            .exclude(comun_id__isnull=True)
            .order_by("comun_id")
            .values_list("comun_id", flat=True)
            .distinct()
        )

        comun_ids: list[int] = []
        seen_comun_ids: set[int] = set()
        for row in through_rows:
            comun_id = int(row.get(comun_field_name) or 0)
            if comun_id <= 0 or comun_id in seen_comun_ids:
                continue
            seen_comun_ids.add(comun_id)
            comun_ids.append(comun_id)
        for comun_id in assignment_comun_ids:
            comun_id = int(comun_id or 0)
            if comun_id <= 0 or comun_id in seen_comun_ids:
                continue
            seen_comun_ids.add(comun_id)
            comun_ids.append(comun_id)

        if not comun_ids:
            continue

        primary_comun_id = comun_ids[0]
        category.comun_id = primary_comun_id
        category.save(update_fields=["comun"])

        if not through_model.objects.filter(
            **{
                comun_field_name: primary_comun_id,
                category_field_name: category.id,
            }
        ).exists():
            through_model.objects.create(
                **{
                    comun_field_name: primary_comun_id,
                    category_field_name: category.id,
                }
            )

        for comun_id in comun_ids[1:]:
            duplicate = ComunCategory.objects.create(
                comun_id=comun_id,
                name=category.name,
                slug=category.slug,
                description=category.description,
                sort_order=category.sort_order,
                is_active=category.is_active,
            )
            through_model.objects.filter(
                **{
                    comun_field_name: comun_id,
                    category_field_name: category.id,
                }
            ).update(**{category_field_name: duplicate.id})
            if not through_model.objects.filter(
                **{
                    comun_field_name: comun_id,
                    category_field_name: duplicate.id,
                }
            ).exists():
                through_model.objects.create(
                    **{
                        comun_field_name: comun_id,
                        category_field_name: duplicate.id,
                    }
                )
            ComunPostCategoryAssignment.objects.filter(
                comun_id=comun_id,
                category_id=category.id,
            ).update(category_id=duplicate.id)


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0075_comun_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='comuncategory',
            name='comun',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owned_categories', to='feeds.comun', verbose_name='Сообщество'),
        ),
        migrations.AlterField(
            model_name='comuncategory',
            name='name',
            field=models.CharField(max_length=120),
        ),
        migrations.AlterField(
            model_name='comuncategory',
            name='slug',
            field=models.SlugField(max_length=120),
        ),
        migrations.RunPython(forwards, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='comuncategory',
            constraint=models.UniqueConstraint(fields=('comun', 'slug'), name='feeds_unique_comun_category_slug_per_comun'),
        ),
        migrations.AddConstraint(
            model_name='comuncategory',
            constraint=models.UniqueConstraint(fields=('comun', 'name'), name='feeds_unique_comun_category_name_per_comun'),
        ),
    ]
