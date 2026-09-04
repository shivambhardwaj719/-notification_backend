from apps.webpush.models import WebPushSubscription
from apps.core.constants.messages import WEBPUSH_SUBSCRIPTION_SUCCESS, WEBPUSH_SUBSCRIPTION_REQUIRED

class SubscriptionService:
    @classmethod
    def subscribe(cls, user, data: dict) -> tuple[bool, str, WebPushSubscription | None]:
        player_id = data.get("player_id") or data.get("subscription_id")
        endpoint = data.get("endpoint")
        browser = data.get("browser", "Chrome")

        if not player_id and not endpoint:
            return False, WEBPUSH_SUBSCRIPTION_REQUIRED, None

        subscription, created = WebPushSubscription.objects.update_or_create(
            user=user,
            defaults={
                "player_id": player_id,
                "subscription_id": player_id,
                "endpoint": endpoint,
                "browser": browser,
                "is_active": True
            }
        )
        return True, WEBPUSH_SUBSCRIPTION_SUCCESS, subscription
