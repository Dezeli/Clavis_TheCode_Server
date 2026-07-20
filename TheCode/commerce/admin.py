from django.contrib import admin
from .models import AdEvent, PurchaseEvent, UserEntitlement, UserStageHintAccess

@admin.register(AdEvent)
class AdEventAdmin(admin.ModelAdmin):
    list_display = ('user', 'stage', 'transaction_id', 'watched_at')
    search_fields = ('user__social_id', 'transaction_id')
    list_filter = ('watched_at',)

@admin.register(UserStageHintAccess)
class UserStageHintAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'stage', 'unlocked_at')
    search_fields = ('user__social_id', 'stage__name')
    list_filter = ('unlocked_at',)

@admin.register(UserEntitlement)
class UserEntitlementAdmin(admin.ModelAdmin):
    list_display = ('user', 'entitlement_type', 'granted_at', 'expires_at')
    search_fields = ('user__social_id', 'entitlement_type')
    list_filter = ('entitlement_type', 'granted_at')


@admin.register(PurchaseEvent)
class PurchaseEventAdmin(admin.ModelAdmin):
    list_display = ('user', 'store', 'product_id', 'order_id', 'verified_at')
    search_fields = (
        'user__provider_user_id',
        'user__email',
        'product_id',
        'order_id',
        'purchase_token',
    )
    list_filter = ('store', 'product_id', 'verified_at')
    readonly_fields = ('payload_json', 'verified_at')
