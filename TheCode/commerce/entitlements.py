from .models import UserEntitlement
from .purchase_products import (
    ALL_ENTITLEMENTS,
    ENTITLEMENT_BANNER_AD_REMOVAL,
    ENTITLEMENT_HINT_AD_REMOVAL,
    ENTITLEMENT_STAGE_UNLOCK,
)


def user_has_entitlement(user, entitlement_type):
    return UserEntitlement.objects.filter(
        user=user,
        entitlement_type=entitlement_type,
        expires_at__isnull=True,
    ).exists()


def serialize_entitlements(user):
    owned = set(
        UserEntitlement.objects.filter(
            user=user,
            entitlement_type__in=ALL_ENTITLEMENTS,
            expires_at__isnull=True,
        ).values_list("entitlement_type", flat=True)
    )

    return {
        "hint_ad_removed": ENTITLEMENT_HINT_AD_REMOVAL in owned,
        "banner_ad_removed": ENTITLEMENT_BANNER_AD_REMOVAL in owned,
        "stage_unlocked": ENTITLEMENT_STAGE_UNLOCK in owned,
        "entitlements": sorted(owned),
    }
