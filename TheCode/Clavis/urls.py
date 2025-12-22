from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/contents/", include("contents.urls")),

    path("admin/", admin.site.urls),
]
