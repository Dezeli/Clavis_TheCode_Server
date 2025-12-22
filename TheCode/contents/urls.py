from django.urls import path
from .views import StageDetailView, StageAnswerView, StageHintView

urlpatterns = [
    path("<int:episode_id>/<int:stage_no>/", StageDetailView.as_view()),
    path("<int:episode_id>/<int:stage_no>/answer/", StageAnswerView.as_view()),
    path("<int:episode_id>/<int:stage_no>/hint/", StageHintView.as_view()),
]
