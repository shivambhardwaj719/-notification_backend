from django.db import IntegrityError
from apps.notifications.models import NotificationTemplate, NotificationTrigger, ChannelChoices, StatusChoices, DeliveryStatusChoices, NotificationDelivery
from apps.notifications.services.variable_service import VariableService
from apps.notifications.services.whatsapp_service import WhatsAppService
from apps.notifications.services.email_service import EmailService
from apps.notifications.services.webpush_service import WebPushService
from apps.webpush.models import WebPushSubscription
from apps.core.constants.messages import (
    TEMPLATE_NOT_FOUND,
    TEMPLATE_UNIQUE_CONSTRAINT_ERROR,
    TEST_RECIPIENT_REQUIRED,
    INVALID_CHANNEL_CHOICE
)

class TemplateService:
    @classmethod
    def get_template_by_id(cls, template_id: int) -> NotificationTemplate | None:
        try:
            return NotificationTemplate.objects.select_related("trigger").get(id=template_id)
        except NotificationTemplate.DoesNotExist:
            return None

    @classmethod
    def create_template(cls, data: dict) -> tuple[bool, str, NotificationTemplate | None]:
        trigger_id = data.get("trigger_id")
        channel = data.get("channel")
        try:
            trigger = NotificationTrigger.objects.get(id=trigger_id)
        except NotificationTrigger.DoesNotExist:
            return False, "Notification trigger not found.", None

        if channel not in ChannelChoices.values:
            return False, INVALID_CHANNEL_CHOICE, None

        if NotificationTemplate.objects.filter(trigger=trigger, channel=channel).exists():
            return False, TEMPLATE_UNIQUE_CONSTRAINT_ERROR, None

        body = data.get("body", "")
        extracted_vars = VariableService.extract_variables(body)

        try:
            template = NotificationTemplate.objects.create(
                trigger=trigger,
                channel=channel,
                name=data.get("name", f"{trigger.code} {channel}"),
                subject=data.get("subject", ""),
                title=data.get("title", ""),
                body=body,
                whatsapp_template_name=data.get("whatsapp_template_name", ""),
                is_enabled=data.get("is_enabled", True),
                status=data.get("status", StatusChoices.ACTIVE),
                variable_mapping={"vars": extracted_vars}
            )
            return True, "", template
        except IntegrityError:
            return False, TEMPLATE_UNIQUE_CONSTRAINT_ERROR, None

    @classmethod
    def update_template(cls, template_id: int, data: dict) -> tuple[bool, str, NotificationTemplate | None]:
        template = cls.get_template_by_id(template_id)
        if not template:
            return False, TEMPLATE_NOT_FOUND, None

        for field in ["name", "subject", "title", "body", "whatsapp_template_name", "is_enabled", "status"]:
            if field in data:
                setattr(template, field, data[field])

        if "body" in data:
            template.variable_mapping = {"vars": VariableService.extract_variables(template.body)}

        template.save()
        return True, "", template

    @classmethod
    def toggle_template(cls, template_id: int) -> tuple[bool, str, NotificationTemplate | None]:
        template = cls.get_template_by_id(template_id)
        if not template:
            return False, TEMPLATE_NOT_FOUND, None

        template.is_enabled = not template.is_enabled
        if not template.is_enabled:
            template.status = StatusChoices.DISABLED
        else:
            template.status = StatusChoices.ACTIVE
        template.save()
        return True, "", template

    @classmethod
    def delete_template(cls, template_id: int) -> tuple[bool, str]:
        template = cls.get_template_by_id(template_id)
        if not template:
            return False, TEMPLATE_NOT_FOUND
        template.delete()
        return True, ""

    @classmethod
    def test_send_template(cls, template_id: int, recipient: str, test_context: dict = None) -> tuple[bool, str, dict]:
        template = cls.get_template_by_id(template_id)
        if not template:
            return False, TEMPLATE_NOT_FOUND, {}

        if not recipient:
            return False, TEST_RECIPIENT_REQUIRED, {}

        ctx = test_context or {
            "user_name": "Test User",
            "user_email": recipient if "@" in recipient else "test@example.com",
            "order_id": "ORD-12345",
            "order_amount": "$99.99",
            "login_time": "2026-09-04 12:00:00 UTC",
            "logout_time": "2026-09-04 13:00:00 UTC",
            "site_name": "SaaS Platform"
        }

        rendered_body = VariableService.render_template(template.body, ctx)
        rendered_subject = VariableService.render_template(template.subject or "", ctx)
        rendered_title = VariableService.render_template(template.title or "", ctx)

        if template.channel == ChannelChoices.WHATSAPP:
            service = WhatsAppService()
            res = service.send(recipient=recipient, content=rendered_body, context=ctx)
        elif template.channel == ChannelChoices.EMAIL:
            service = EmailService()
            res = service.send(recipient=recipient, content=rendered_body, subject=rendered_subject, context=ctx)
        elif template.channel == ChannelChoices.WEB_PUSH:
            service = WebPushService()
            res = service.send(recipient=recipient, content=rendered_body, title=rendered_title, context=ctx)
        else:
            return False, INVALID_CHANNEL_CHOICE, {}

        delivery_status = DeliveryStatusChoices.SENT if res["success"] else DeliveryStatusChoices.FAILED
        delivery = NotificationDelivery.objects.create(
            trigger=template.trigger,
            template=template,
            channel=template.channel,
            status=delivery_status,
            provider_message_id=res.get("provider_message_id"),
            error_message=res.get("error_message")
        )

        return res["success"], res.get("error_message") or "Test send completed successfully.", {
            "delivery_id": delivery.id,
            "provider_message_id": res.get("provider_message_id"),
            "status": delivery_status,
            "rendered_content": rendered_body
        }
