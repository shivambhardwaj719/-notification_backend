from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.authentication.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("api/webpush/", include("apps.webpush.urls")),
]
