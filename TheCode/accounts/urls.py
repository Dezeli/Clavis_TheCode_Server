from django.urls import path
from .views import GoogleLoginURLView, GoogleAuthCallbackView, GoogleTestRedirectView

urlpatterns = [
    path("google/login-url/", GoogleLoginURLView.as_view()),
    path("google/callback/", GoogleAuthCallbackView.as_view()),
    path("google/redirect-test", GoogleTestRedirectView.as_view()),
]
