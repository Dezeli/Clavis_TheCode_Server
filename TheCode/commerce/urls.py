from django.urls import path
from .views import AdMobSSVView

urlpatterns = [
    path('admob-ssv/', AdMobSSVView.as_view(), name='admob-ssv'),
]