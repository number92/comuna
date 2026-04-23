from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("feeds", "0092_backfill_toc_template_block"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="sitenotificationpreference",
            name="push_enabled",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="sitenotification",
            name="is_push",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="sitenotification",
            name="push_error",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="sitenotification",
            name="push_sent_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="MobilePushDevice",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("token", models.CharField(max_length=512, unique=True)),
                (
                    "platform",
                    models.CharField(
                        choices=[("ios", "iOS"), ("android", "Android")],
                        max_length=20,
                    ),
                ),
                ("device_id", models.CharField(blank=True, max_length=191)),
                ("device_name", models.CharField(blank=True, max_length=120)),
                ("app_version", models.CharField(blank=True, max_length=40)),
                ("is_active", models.BooleanField(default=True)),
                ("last_seen_at", models.DateTimeField(auto_now=True)),
                ("last_push_sent_at", models.DateTimeField(blank=True, null=True)),
                ("last_error", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mobile_push_devices",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Push-устройство",
                "verbose_name_plural": "Push-устройства",
                "ordering": ("platform", "-last_seen_at", "-id"),
            },
        ),
        migrations.AddIndex(
            model_name="sitenotification",
            index=models.Index(fields=["user", "is_push"], name="feeds_siteno_user_id_c6eaa2_idx"),
        ),
        migrations.AddIndex(
            model_name="mobilepushdevice",
            index=models.Index(fields=["user", "is_active"], name="feeds_mobile_user_id_680b49_idx"),
        ),
        migrations.AddIndex(
            model_name="mobilepushdevice",
            index=models.Index(
                fields=["user", "platform", "is_active"],
                name="feeds_mobile_user_id_94bb37_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="mobilepushdevice",
            index=models.Index(fields=["user", "device_id"], name="feeds_mobile_user_id_9a5736_idx"),
        ),
    ]
