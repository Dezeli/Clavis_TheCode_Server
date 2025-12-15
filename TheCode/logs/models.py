from accounts.models import User
from contents.models import Stage
from django.db import models

class AppAccessLog(models.Model):
    EVENT_TYPE_CHOICES = [
        ("app_open", "App Open"),
        ("app_background", "App Background"),
        ("app_foreground", "App Foreground"),
    ]

    PLATFORM_CHOICES = [
        ("android", "Android"),
        ("ios", "iOS"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="app_access_logs",
    )

    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPE_CHOICES,
    )

    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
    )

    app_version = models.CharField(max_length=50)
    device_info = models.CharField(max_length=255, blank=True)

    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-occurred_at"]

    def __str__(self):
        return f"{self.user} - {self.event_type} ({self.platform})"


class StageActivityLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="stage_activity_logs",
    )

    stage = models.ForeignKey(
        Stage,
        on_delete=models.CASCADE,
        related_name="activity_logs",
    )

    entered_at = models.DateTimeField()
    exited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-entered_at"]

    def __str__(self):
        return f"{self.user} - {self.stage}"
