from django.contrib import admin
from progress.models import UserEpisodeProgress

@admin.register(UserEpisodeProgress)
class UserEpisodeProgressAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "episode",
        "current_stage_no",
        "highest_stage_no",
        "is_cleared",
        "started_at",
        "cleared_at",
    )
    list_filter = ("is_cleared", "episode")
    search_fields = ("user__email", "user__username")
