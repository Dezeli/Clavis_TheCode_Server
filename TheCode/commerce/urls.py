from django.urls import path
from .views import (
    AdMobSSVView,
    EntitlementStatusView,
    GooglePlayPurchaseVerifyView,
    HintAccessStatusView,
)

urlpatterns = [
    path('admob-ssv/', AdMobSSVView.as_view(), name='admob-ssv'),
    path('entitlements/', EntitlementStatusView.as_view(), name='entitlement-status'),
    path(
        'purchases/google/verify/',
        GooglePlayPurchaseVerifyView.as_view(),
        name='google-play-purchase-verify',
    ),
    path(
        'hint-access/<int:episode_id>/<int:stage_no>/',
        HintAccessStatusView.as_view(),
        name='hint-access-status',
    ),
]
