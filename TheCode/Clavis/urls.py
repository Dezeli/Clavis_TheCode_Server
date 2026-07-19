from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/contents/", include("contents.urls")),
    path("api/v1/commerce/", include("commerce.urls")),
    path("api/v1/progress/", include("progress.urls")),

    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
