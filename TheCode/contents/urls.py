from django.urls import path
from .views import StageImageProxyView

urlpatterns = [
    path("stages/<int:stage_id>/image/", StageImageProxyView.as_view()),
]
