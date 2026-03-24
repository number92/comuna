from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("feeds", "0081_comun_source_tags"),
    ]

    operations = [
        migrations.AddField(
            model_name="comun",
            name="forbid_external_links",
            field=models.BooleanField(
                default=False,
                help_text="Если включено, посты с внешними ссылками не будут попадать в сообщество, а новые публикации с такими ссылками будут отклоняться.",
                verbose_name="Запретить внешние ссылки",
            ),
        ),
    ]
