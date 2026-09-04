from rest_framework import serializers
from apps.webpush.models import WebPushSubscription

class WebPushSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebPushSubscription
        fields = ["id", "user", "subscription_id", "player_id", "browser", "endpoint", "is_active", "created_at"]
        read_only_fields = ["id", "user", "created_at"]
