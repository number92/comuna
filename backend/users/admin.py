from django.contrib import admin

from users.models import AuthorAdmin as AuthorAdminLink, AuthorVerificationCode


@admin.register(AuthorAdminLink)
class AuthorAdminLinkAdmin(admin.ModelAdmin):
    list_display = ("author", "user", "verified_at", "created_at")
    search_fields = ("author__username", "user__username")
    raw_id_fields = ("author", "user")


@admin.register(AuthorVerificationCode)
class AuthorVerificationCodeAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "used_at", "created_at")
    search_fields = ("user__username", "code")
    raw_id_fields = ("user",)


