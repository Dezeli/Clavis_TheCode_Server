from django.urls import path
from .views import GoogleLoginView, DevTestLoginView, RefreshTokenView, LogoutView, MeView

urlpatterns = [
    path("google/login/", GoogleLoginView.as_view()),
    path("dev/login/", DevTestLoginView.as_view()),
    path("refresh/", RefreshTokenView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("me/", MeView.as_view()),
]
