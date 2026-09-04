from django.urls import path
from apps.webpush.views import WebPushSubscribeView

urlpatterns = [
    path("subscribe/", WebPushSubscribeView.as_view(), name="webpush-subscribe"),
]
