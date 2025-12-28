from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import User, StoredRefreshToken


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    ordering = ("id",)

    class Media:
        css = {
            "all": ("admin/custom.css",)
        }

    list_display = (
        "colored_id",
        "username",
        "email",
        "colored_provider",
        "provider_user_id",
        "is_staff",
        "is_active",
        "created_at",
        "edit_button",
    )

    list_display_links = None

    list_filter = (
        "provider",
        "is_staff",
        "is_active",
        "created_at",
    )

    search_fields = (
        "username",
        "email",
        "provider_user_id",
    )

    list_per_page = 25

    readonly_fields = (
        "provider",
        "provider_user_id",
        "created_at",
        "last_login_at",
    )

    fieldsets = (
        ("기본 정보", {
            "fields": (
                "provider",
                "provider_user_id",
                "username",
                "email",
            )
        }),
        ("권한", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
            )
        }),
        ("접속 정보", {
            "fields": (
                "last_login_at",
                "created_at",
            )
        }),
    )

    @admin.display(description="ID", ordering="id")
    def colored_id(self, obj):
        color_map = {
            "apple": "#e74c3c",    # 빨강
            "google": "#5dade2",   # 하늘
            "local": "#2ecc71",    # 초록
        }
        color = color_map.get(obj.provider, "#7f8c8d")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.id,
        )

    @admin.display(description="provider")
    def colored_provider(self, obj):
        color_map = {
            "apple": "#e74c3c",    # 빨강
            "google": "#5dade2",   # 하늘
            "local": "#2ecc71",    # 초록
        }
        color = color_map.get(obj.provider, "#7f8c8d")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.provider,
        )
    
    @admin.display(description="Edit")
    def edit_button(self, obj):
        url = reverse("admin:accounts_user_change", args=[obj.pk])
        return format_html(
            '<a href="{}" style="'
            'padding:4px 10px; '
            'background:#34495e; '
            'color:skyblue; '
            'border-radius:4px; '
            'font-weight:600; '
            'text-decoration:none;'
            '">Edit</a>',
            url,
        )


@admin.register(StoredRefreshToken)
class StoredRefreshTokenAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)

    class Media:
        css = {
            "all": ("admin/custom.css",)
        }

    list_display = (
        "colored_id",
        "colored_user",
        "colored_session_scope",
        "device_info",
        "colored_revoked",
        "expires_at",
        "created_at",
        "edit_button",
    )

    list_display_links = None

    list_filter = (
        "revoked",
        "session_scope",
        "created_at",
        "expires_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "device_info",
        "token",
    )

    list_per_page = 25

    readonly_fields = (
        "user",
        "token",
        "created_at",
    )

    fieldsets = (
        ("기본 정보", {
            "fields": (
                "user",
                "session_scope",
                "device_info",
            )
        }),
        ("토큰 상태", {
            "fields": (
                "revoked",
                "expires_at",
            )
        }),
        ("메타 정보", {
            "fields": (
                "token",
                "created_at",
            )
        }),
    )

    def _provider_color(self, provider):
        return {
            "apple": "#e74c3c",   # 빨강
            "google": "#5dade2",  # 하늘
            "local": "#2ecc71",   # 초록
        }.get(provider, "#7f8c8d")

    def _session_scope_color(self, scope):
        return {
            "apple": "#e74c3c",   # 빨강
            "google": "#5dade2",  # 하늘
            "local": "#2ecc71",   # 초록
        }.get(scope, "#95a5a6")  # 기본 회색

    @admin.display(description="ID", ordering="id")
    def colored_id(self, obj):
        color = "#b0b0b0" if obj.revoked else self._provider_color(obj.user.provider)
        return format_html(
            '<span style="color:{}; font-weight:600;">{}</span>',
            color,
            obj.id,
        )

    @admin.display(description="User")
    def colored_user(self, obj):
        color = "#b0b0b0" if obj.revoked else self._provider_color(obj.user.provider)
        return format_html(
            '<span style="color:{}; font-weight:600;">{}. {}</span>',
            color,
            obj.user.id,
            obj.user.username or "-",
        )

    @admin.display(description="Session Scope")
    def colored_session_scope(self, obj):
        color = "#b0b0b0" if obj.revoked else self._session_scope_color(obj.session_scope)
        return format_html(
            '<span style="color:{}; font-weight:600;">{}</span>',
            color,
            obj.session_scope,
        )

    @admin.display(description="revoked", boolean=True)
    def colored_revoked(self, obj):
        return obj.revoked

    @admin.display(description="Edit")
    def edit_button(self, obj):
        url = reverse("admin:accounts_storedrefreshtoken_change", args=[obj.pk])
        return format_html(
            '<a href="{}" style="'
            'padding:4px 10px; '
            'background:#34495e; '
            'color:skyblue; '
            'border-radius:4px; '
            'font-weight:600; '
            'text-decoration:none;'
            '">Edit</a>',
            url,
        )