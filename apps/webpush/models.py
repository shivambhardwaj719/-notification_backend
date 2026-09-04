from django.db import models
from django.conf import settings

class WebPushSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="webpush_subscriptions")
    subscription_id = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    player_id = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    browser = models.CharField(max_length=50, blank=True, default="Chrome")
    endpoint = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "web_push_subscriptions"
        indexes = [
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"WebPushSub {self.user.username} ({self.player_id or self.subscription_id})"
