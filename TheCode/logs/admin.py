from django.contrib import admin
from logs.models import AppAccessLog, StageActivityLog

@admin.register(AppAccessLog)
class AppAccessLogAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "event_type",
        "platform",
        "app_version",
        "occurred_at",
    )
    list_filter = ("platform", "event_type")
    search_fields = ("user__email",)

@admin.register(StageActivityLog)
class StageActivityLogAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "stage",
        "entered_at",
        "exited_at",
    )
    list_filter = ("stage",)
