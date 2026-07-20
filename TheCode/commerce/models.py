from accounts.models import User
from contents.models import Stage 
from django.db import models


class PurchaseEvent(models.Model):
    STORE_GOOGLE_PLAY = "google_play"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    store = models.CharField(max_length=30, default=STORE_GOOGLE_PLAY)
    product_id = models.CharField(max_length=100)
    purchase_token = models.CharField(max_length=512, unique=True)
    order_id = models.CharField(max_length=255, null=True, blank=True)
    payload_json = models.JSONField(default=dict)
    verified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "product_id"]),
            models.Index(fields=["order_id"]),
        ]

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
