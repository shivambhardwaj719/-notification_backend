from celery import shared_task
from django.utils import timezone
from apps.notifications.models import NotificationDelivery, DeliveryStatusChoices
from apps.notifications.services.whatsapp_service import WhatsAppService
from apps.notifications.services.email_service import EmailService
from apps.notifications.services.webpush_service import WebPushService

@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def send_whatsapp_notification(self, delivery_id: int, recipient: str, body: str, context: dict = None):
    try:
        delivery = NotificationDelivery.objects.get(id=delivery_id)
    except NotificationDelivery.DoesNotExist:
        return

    service = WhatsAppService()
    result = service.send(recipient=recipient, content=body, context=context)

    if result["success"]:
        delivery.status = DeliveryStatusChoices.SENT
        delivery.provider_message_id = result["provider_message_id"]
        delivery.sent_at = timezone.now()
        delivery.save()
    else:
        delivery.error_message = result["error_message"]
        if self.request.retries < self.max_retries:
            delivery.save()
            raise self.retry(exc=Exception(result["error_message"]))
        else:
            delivery.status = DeliveryStatusChoices.FAILED
            delivery.save()

@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def send_email_notification(self, delivery_id: int, recipient: str, body: str, subject: str = None, context: dict = None):
    try:
        delivery = NotificationDelivery.objects.get(id=delivery_id)
    except NotificationDelivery.DoesNotExist:
        return

    service = EmailService()
    result = service.send(recipient=recipient, content=body, subject=subject, context=context)

    if result["success"]:
        delivery.status = DeliveryStatusChoices.SENT
        delivery.provider_message_id = result["provider_message_id"]
        delivery.sent_at = timezone.now()
        delivery.save()
    else:
        delivery.error_message = result["error_message"]
        if self.request.retries < self.max_retries:
            delivery.save()
            raise self.retry(exc=Exception(result["error_message"]))
        else:
            delivery.status = DeliveryStatusChoices.FAILED
            delivery.save()

@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def send_webpush_notification(self, delivery_id: int, recipient: str, body: str, title: str = None, context: dict = None):
    try:
        delivery = NotificationDelivery.objects.get(id=delivery_id)
    except NotificationDelivery.DoesNotExist:
        return

    service = WebPushService()
    result = service.send(recipient=recipient, content=body, title=title, context=context)

    if result["success"]:
        delivery.status = DeliveryStatusChoices.SENT
        delivery.provider_message_id = result["provider_message_id"]
        delivery.sent_at = timezone.now()
        delivery.save()
    else:
        delivery.error_message = result["error_message"]
        if self.request.retries < self.max_retries:
            delivery.save()
            raise self.retry(exc=Exception(result["error_message"]))
        else:
            delivery.status = DeliveryStatusChoices.FAILED
            delivery.save()
