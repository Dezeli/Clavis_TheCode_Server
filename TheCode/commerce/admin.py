from django.contrib import admin
from .models import AdEvent, UserStageHintAccess, UserEntitlement

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