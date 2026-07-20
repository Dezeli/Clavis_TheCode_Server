from django.urls import path
from .views import AdMobSSVView, HintAccessStatusView

urlpatterns = [
    path('admob-ssv/', AdMobSSVView.as_view(), name='admob-ssv'),
    path(
        'hint-access/<int:episode_id>/<int:stage_no>/',
        HintAccessStatusView.as_view(),
        name='hint-access-status',
    ),
]
