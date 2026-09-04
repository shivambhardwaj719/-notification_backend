from apps.notifications.models import NotificationDelivery

class DeliveryService:
    @classmethod
    def list_deliveries(cls, user_id: int = None, trigger_code: str = None, status: str = None, channel: str = None):
        queryset = NotificationDelivery.objects.select_related("user", "trigger", "template").all()
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if trigger_code:
            queryset = queryset.filter(trigger__code=trigger_code)
        if status:
            queryset = queryset.filter(status=status)
        if channel:
            queryset = queryset.filter(channel=channel)
        return queryset[:100]
