from django.urls import path
from .views import GoogleLoginView, RefreshTokenView, LogoutView

urlpatterns = [
    path("google/login/", GoogleLoginView.as_view()),
    path("refresh/", RefreshTokenView.as_view()),
    path("logout/", LogoutView.as_view()),
]
