from django.urls import path
from .views import StartStageView, StageDetailView, StageAnswerView, StageHintView

urlpatterns = [
    path("start/", StartStageView.as_view()),
    path("<int:episode_id>/<int:stage_no>/", StageDetailView.as_view()),
    path("<int:episode_id>/<int:stage_no>/answer/", StageAnswerView.as_view()),
    path("<int:episode_id>/<int:stage_no>/hint/", StageHintView.as_view()),
]
