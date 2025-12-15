from accounts.models import User
from contents.models import Episode, Stage 
from django.db import models

class UserStageHintAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)

    unlock_source = models.CharField(
        max_length=50,
        help_text="ad / episode_purchase / premium_pass",
    )
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "stage")

    def __str__(self):
        return f"{self.user} unlocked hint for {self.stage}"


class UserEntitlement(models.Model):
    TYPE_CHOICES = [
        ("episode_unlock_stages", "Episode Unlock Stages"),
        ("episode_unlock_with_adfree", "Episode Unlock + Adfree"),
        ("premium_pass", "Premium Pass"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)

    episode = models.ForeignKey(
        Episode,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "type", "episode")

    def __str__(self):
        return f"{self.user} - {self.type}"


class AdEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)

    ad_network = models.CharField(max_length=50)
    reward_type = models.CharField(max_length=50)
    reward_amount = models.IntegerField()

    watched_at = models.DateTimeField(auto_now_add=True)


class PaymentEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)

    event_type = models.CharField(max_length=20)
    store = models.CharField(max_length=20)
    product_id = models.CharField(max_length=100)

    amount = models.IntegerField()
    currency = models.CharField(max_length=10)

    payload_json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)