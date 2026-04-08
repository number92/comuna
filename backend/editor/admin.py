from django import forms
from django.contrib import admin

from editor.models import (
    POST_TEMPLATE_TYPE_CHOICES,
    PostTemplateConfig,
    default_enabled_template_editor_blocks,
    normalize_template_editor_blocks_for_template,
    template_editor_block_choices_for_template,
)


class PostTemplateConfigAdminForm(forms.ModelForm):
    enabled_editor_blocks = forms.MultipleChoiceField(
        label="Доступные блоки редактора",
        choices=(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Отмеченные блоки будут доступны в редакторе для этого шаблона.",
    )

    class Meta:
        model = PostTemplateConfig
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        template_type = (
            str(
                self.instance.template_type
                or self.initial.get("template_type")
                or self.data.get("template_type")
                or ""
            )
            .strip()
            .lower()
        )
        choices = template_editor_block_choices_for_template(template_type)
        self.fields["enabled_editor_blocks"].choices = choices
        self.fields["enabled_editor_blocks"].initial = normalize_template_editor_blocks_for_template(
            template_type,
            getattr(self.instance, "enabled_editor_blocks", None)
            or default_enabled_template_editor_blocks(template_type),
        )

    def clean_enabled_editor_blocks(self):
        template_type = str(self.cleaned_data.get("template_type") or "").strip().lower()
        return normalize_template_editor_blocks_for_template(
            template_type, self.cleaned_data.get("enabled_editor_blocks")
        )


@admin.register(PostTemplateConfig)
class PostTemplateConfigAdmin(admin.ModelAdmin):
    form = PostTemplateConfigAdminForm
    list_display = (
        "template_type",
        "enabled_editor_blocks_display",
        "updated_at",
    )
    fields = (
        "template_type",
        "enabled_editor_blocks",
    )
    readonly_fields = ("template_type",)

    def get_queryset(self, request):
        PostTemplateConfig.ensure_defaults()
        return super().get_queryset(request)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def enabled_editor_blocks_display(self, obj):
        choices = dict(template_editor_block_choices_for_template(obj.template_type))
        values = normalize_template_editor_blocks_for_template(
            obj.template_type, obj.enabled_editor_blocks
        )
        labels = [choices.get(value, value) for value in values]
        return ", ".join(labels) if labels else "Без дополнительных блоков"

    enabled_editor_blocks_display.short_description = "Блоки редактора"

