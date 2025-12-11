from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, StoredRefreshToken


class UserAdmin(BaseUserAdmin):
    list_display = ("id", "email", "provider", "provider_user_id", "username", "created_at", "last_login_at", "is_active")
    list_filter = ("provider", "is_active")
    search_fields = ("email", "provider_user_id", "username")

    ordering = ("-created_at",)

    fieldsets = (
        ("기본 정보", {"fields": ("email", "username")}),
        ("소셜 로그인 정보", {"fields": ("provider", "provider_user_id")}),
        ("권한", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("중요 시각", {"fields": ("last_login_at", "created_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "provider", "provider_user_id", "password1", "password2"),
            },
        ),
    )


admin.site.register(User, UserAdmin)


@admin.register(StoredRefreshToken)
class StoredRefreshTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_scope", "revoked", "expires_at", "created_at")
    list_filter = ("session_scope", "revoked")
    search_fields = ("user__email", "token")
    ordering = ("-created_at",)
