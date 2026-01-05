from accounts.models import User
from contents.models import Stage 
from django.db import models

class AdEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=255, unique=True)
    watched_at = models.DateTimeField(auto_now_add=True)


class UserStageHintAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    ad_event = models.OneToOneField(AdEvent, on_delete=models.CASCADE, null=True)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "stage")


class UserEntitlement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    entitlement_type = models.CharField(max_length=50) 
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)