from apps.notifications.models import NotificationTrigger, NotificationTemplate, NotificationDelivery, ChannelChoices, DeliveryStatusChoices
from apps.notifications.services.variable_service import VariableService
from apps.notifications.tasks import send_whatsapp_notification, send_email_notification, send_webpush_notification
from apps.webpush.models import WebPushSubscription
from apps.core.constants.messages import PROVIDER_DISABLED_SKIPPED, TRIGGER_NOT_FOUND

class NotificationService:
    @classmethod
    def trigger(cls, trigger_code: str, user=None, context: dict = None) -> tuple[bool, str, list[dict]]:
        try:
            trigger_obj = NotificationTrigger.objects.prefetch_related("templates").get(code=trigger_code, is_active=True)
        except NotificationTrigger.DoesNotExist:
            return False, TRIGGER_NOT_FOUND, []

        ctx = context or {}
        if user:
            ctx.setdefault("user_name", user.get_full_name() or user.username)
            ctx.setdefault("user_email", user.email or "")

        results = []
        enabled_templates = {t.channel: t for t in trigger_obj.templates.all()}

        for channel in [ChannelChoices.WHATSAPP, ChannelChoices.EMAIL, ChannelChoices.WEB_PUSH]:
            tmpl = enabled_templates.get(channel)

            if not tmpl or not tmpl.is_enabled:
                delivery = NotificationDelivery.objects.create(
                    user=user,
                    trigger=trigger_obj,
                    template=tmpl,
                    channel=channel,
                    status=DeliveryStatusChoices.SKIPPED,
                    error_message=PROVIDER_DISABLED_SKIPPED
                )
                results.append({
                    "channel": channel,
                    "status": DeliveryStatusChoices.SKIPPED,
                    "delivery_id": delivery.id
                })
                continue

            rendered_body = VariableService.render_template(tmpl.body, ctx)
            rendered_subject = VariableService.render_template(tmpl.subject or "", ctx)
            rendered_title = VariableService.render_template(tmpl.title or "", ctx)

            delivery = NotificationDelivery.objects.create(
                user=user,
                trigger=trigger_obj,
                template=tmpl,
                channel=channel,
                status=DeliveryStatusChoices.PENDING
            )

            recipient = None
            if channel == ChannelChoices.WHATSAPP:
                recipient = ctx.get("phone") or getattr(user, "phone", None) or getattr(user, "username", "mock_phone")
                send_whatsapp_notification.delay(
                    delivery_id=delivery.id,
                    recipient=recipient,
                    body=rendered_body,
                    context=ctx
                )
            elif channel == ChannelChoices.EMAIL:
                recipient = ctx.get("user_email") or getattr(user, "email", "test@example.com")
                send_email_notification.delay(
                    delivery_id=delivery.id,
                    recipient=recipient,
                    body=rendered_body,
                    subject=rendered_subject,
                    context=ctx
                )
            elif channel == ChannelChoices.WEB_PUSH:
                sub = None
                if user:
                    sub = WebPushSubscription.objects.filter(user=user, is_active=True).first()
                recipient = sub.player_id if sub else (ctx.get("player_id") or "mock_player_id")
                send_webpush_notification.delay(
                    delivery_id=delivery.id,
                    recipient=recipient,
                    body=rendered_body,
                    title=rendered_title,
                    context=ctx
                )

            results.append({
                "channel": channel,
                "status": DeliveryStatusChoices.PENDING,
                "delivery_id": delivery.id
            })

        return True, "Notification triggers processed successfully.", results
