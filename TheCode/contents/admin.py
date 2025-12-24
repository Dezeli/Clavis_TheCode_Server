from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from contents.models import Series, Episode, Stage, Hint


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    ordering = ("code",)

    class Media:
        css = {
            "all": ("admin/custom.css",)
        }

    list_display = (
        "colored_code",
        "colored_title",
        "short_description",
        "colored_active",
        "created_at",
        "edit_button",
    )

    list_display_links = None

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "code",
        "title",
        "description",
    )

    list_per_page = 25

    readonly_fields = (
        "created_at",
    )

    fieldsets = (
        ("기본 정보", {
            "fields": (
                "code",
                "title",
                "description",
            )
        }),
        ("상태", {
            "fields": (
                "is_active",
            )
        }),
        ("메타 정보", {
            "fields": (
                "created_at",
            )
        }),
    )

    @admin.display(description="Code", ordering="code")
    def colored_code(self, obj):
        color = "#2ecc71" if obj.is_active else "#b0b0b0"
        return format_html(
            '<span style="color:{}; font-weight:700;">{}</span>',
            color,
            obj.code,
        )

    @admin.display(description="Title", ordering="title")
    def colored_title(self, obj):
        color = "#2ecc71" if obj.is_active else "#b0b0b0"
        return format_html(
            '<span style="color:{}; font-weight:700;">{}</span>',
            color,
            obj.title,
        )

    @admin.display(description="Description")
    def short_description(self, obj):
        if not obj.description:
            return "-"
        return obj.description[:50] + ("…" if len(obj.description) > 50 else "")

    @admin.display(description="Active", boolean=True)
    def colored_active(self, obj):
        return obj.is_active
    
    @admin.display(description="Edit")
    def edit_button(self, obj):
        url = reverse("admin:contents_series_change", args=[obj.pk])
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


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    ordering = ("code",)

    class Media:
        css = {
            "all": ("admin/custom.css",)
        }

    list_display = (
        "colored_code",
        "colored_series",
        "colored_title",
        "price_unlock_stages",
        "price_unlock_with_adfree",
        "colored_released",
        "created_at",
        "edit_button",
    )

    list_display_links = None

    list_filter = (
        "series",
        "is_released",
        "created_at",
    )

    search_fields = (
        "code",
        "title",
        "series__title",
        "series__code",
    )

    list_per_page = 25

    readonly_fields = (
        "created_at",
    )

    fieldsets = (
        ("기본 정보", {
            "fields": (
                "series",
                "code",
                "title",
                "description",
            )
        }),
        ("출시 상태", {
            "fields": (
                "is_released",
            )
        }),
        ("가격 정보", {
            "fields": (
                "price_unlock_stages",
                "price_unlock_with_adfree",
            )
        }),
        ("메타 정보", {
            "fields": (
                "created_at",
            )
        }),
    )

    def _active_color(self, released):
        return "#2ecc71" if released else "#b0b0b0"

    @admin.display(description="Code", ordering="code")
    def colored_code(self, obj):
        color = self._active_color(obj.is_released)
        return format_html(
            '<span style="color:{}; font-weight:700;">{}</span>',
            color,
            obj.code,
        )

    @admin.display(description="Title", ordering="title")
    def colored_title(self, obj):
        color = self._active_color(obj.is_released)
        return format_html(
            '<span style="color:{}; font-weight:700;">{}</span>',
            color,
            obj.title,
        )

    @admin.display(description="Series")
    def colored_series(self, obj):
        color = self._active_color(obj.is_released)
        return format_html(
            '<span style="color:{}; font-weight:600;">{}</span>',
            color,
            obj.series.title,
        )

    @admin.display(description="Released", boolean=True)
    def colored_released(self, obj):
        return obj.is_released
    
    @admin.display(description="Edit")
    def edit_button(self, obj):
        url = reverse("admin:contents_episode_change", args=[obj.pk])
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
    
@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    ordering = ("episode__code", "stage_no")

    class Media:
        css = {
            "all": ("admin/custom.css",)
        }

    list_display = (
        "colored_episode",
        "colored_stage_no",
        "colored_title",
        "colored_answer",
        "colored_free",
        "next_stage_no",
        "created_at",
        "edit_button",
    )

    list_display_links = None

    list_filter = (
        "episode__series",
        "episode",
        "is_free",
        "created_at",
    )

    search_fields = (
        "title",
        "answer_text",
        "episode__title",
        "episode__code",
        "episode__series__title",
    )

    list_per_page = 50

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("기본 정보", {
            "fields": (
                "episode",
                "stage_no",
                "title",
                "is_free",
            )
        }),
        ("문제 데이터", {
            "fields": (
                "image_key",
                "answer_text",
                "next_stage",
            )
        }),
        ("메타 정보", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )

    @admin.display(description="Episode", ordering="episode__code")
    def colored_episode(self, obj):
        color = "#2ecc71" if obj.is_free else "#5dade2"
        return format_html(
            '<span style="color:{}; font-weight:600;">{} / {}</span>',
            color,
            obj.episode.series.title,
            obj.episode.title,
        )

    @admin.display(description="Stage No", ordering="stage_no")
    def colored_stage_no(self, obj):
        color = "#2ecc71" if obj.is_free else "#5dade2"
        return format_html(
            '<span style="color:{}; font-weight:700;">{}</span>',
            color,
            obj.stage_no,
        )

    @admin.display(description="Title")
    def colored_title(self, obj):
        color = "#2ecc71" if obj.is_free else "#5dade2"
        return format_html(
            '<span style="color:{}; font-weight:600;">{}</span>',
            color,
            obj.title,
        )

    @admin.display(description="Answer")
    def colored_answer(self, obj):
        return format_html(
            '<span style="font-family:monospace; font-weight:600;">{}</span>',
            obj.answer_text,
        )

    @admin.display(description="Free", boolean=True)
    def colored_free(self, obj):
        return obj.is_free

    @admin.display(description="Next")
    def next_stage_no(self, obj):
        if not obj.next_stage:
            return "-"

        color = "#2ecc71" if obj.next_stage.is_free else "#5dade2"

        return format_html(
            '<span style="color:{}; font-weight:600;">{} / {}</span>',
            color,
            obj.next_stage.episode.title,
            obj.next_stage.title,
        )

    @admin.display(description="Edit")
    def edit_button(self, obj):
        url = reverse("admin:contents_stage_change", args=[obj.pk])
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

@admin.register(Hint)
class HintAdmin(admin.ModelAdmin):
    ordering = ("stage__episode__code", "stage__stage_no")

    class Media:
        css = {
            "all": ("admin/custom.css",)
        }

    list_display = (
        "colored_episode",
        "colored_stage_no",
        "short_content",
        "edit_button",
    )

    list_display_links = None

    list_filter = (
        "stage__episode__series",
        "stage__episode",
    )

    search_fields = (
        "content",
        "stage__title",
        "stage__episode__title",
        "stage__episode__code",
    )

    list_per_page = 50

    fieldsets = (
        ("연결 정보", {
            "fields": (
                "stage",
            )
        }),
        ("힌트 내용", {
            "fields": (
                "content",
            )
        }),
    )

    @admin.display(description="Episode", ordering="stage__episode__code")
    def colored_episode(self, obj):
        color = "#2ecc71" if obj.stage.is_free else "#5dade2"
        return format_html(
            '<span style="color:{}; font-weight:600;">{} / {}</span>',
            color,
            obj.stage.episode.series.title,
            obj.stage.episode.title,
        )

    @admin.display(description="Stage")
    def colored_stage_no(self, obj):
        color = "#2ecc71" if obj.stage.is_free else "#5dade2"
        return format_html(
            '<span style="color:{}; font-weight:700;">{}. {}</span>',
            color,
            obj.stage.stage_no,
            obj.stage.title,
        )

    @admin.display(description="Hint")
    def short_content(self, obj):
        text = obj.content.strip()
        return text[:40] + ("…" if len(text) > 40 else "")

    @admin.display(description="Edit")
    def edit_button(self, obj):
        url = reverse("admin:contents_hint_change", args=[obj.pk])
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