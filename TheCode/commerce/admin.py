from django.contrib import admin
from commerce.models import (
    UserEntitlement,
    PaymentEvent,
    AdEvent,
    UserStageHintAccess,
)

@admin.register(UserEntitlement)
class UserEntitlementAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "type",
        "episode",
        "granted_at",
        "expires_at",
    )
    list_filter = ("type",)
    search_fields = ("user__email", "user__username")

@admin.register(PaymentEvent)
class PaymentEventAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "episode",
        "event_type",
        "store",
        "amount",
        "currency",
        "created_at",
    )
    list_filter = ("event_type", "store")
    search_fields = ("user__email", "product_id")

@admin.register(AdEvent)
class AdEventAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "stage",
        "ad_network",
        "reward_type",
        "reward_amount",
        "watched_at",
    )
    list_filter = ("ad_network", "reward_type")

@admin.register(UserStageHintAccess)
class UserStageHintAccessAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "stage",
        "unlock_source",
        "unlocked_at",
    )
    list_filter = ("unlock_source",)
    search_fields = ("user__email",)
