from accounts.models import User
from contents.models import Episode
from django.db import models


class UserEpisodeProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)

    current_stage_no = models.PositiveIntegerField(default=1)
    highest_stage_no = models.PositiveIntegerField(default=1)

    is_cleared = models.BooleanField(default=False)

    started_at = models.DateTimeField(auto_now_add=True)
    cleared_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "episode")

    def __str__(self):
        return f"{self.user} - {self.episode}"
