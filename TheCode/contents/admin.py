from django.contrib import admin
from contents.models import Series, Episode, Stage, Hint

@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("code", "title")
    ordering = ("created_at",)

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "title",
        "series",
        "is_released",
        "price_unlock_stages",
        "price_unlock_with_adfree",
        "created_at",
    )
    list_filter = ("is_released", "series")
    search_fields = ("code", "title")
    ordering = ("created_at",)

@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = (
        "episode",
        "stage_no",
        "title",
        "is_free",
        "next_stage",
        "created_at",
    )
    list_filter = ("episode", "is_free")
    search_fields = ("title",)
    ordering = ("episode", "stage_no")

    readonly_fields = ("created_at", "updated_at")

@admin.register(Hint)
class HintAdmin(admin.ModelAdmin):
    list_display = ("stage",)
    search_fields = ("stage__title",)
