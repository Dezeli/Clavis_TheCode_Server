from django.urls import path

from .views import CompleteStageView, ProgressStartView

urlpatterns = [
    path("start/", ProgressStartView.as_view()),
    path("complete-stage/", CompleteStageView.as_view()),
]
