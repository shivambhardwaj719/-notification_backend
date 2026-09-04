from apps.notifications.models import NotificationTrigger, ChannelChoices
from apps.core.constants.messages import TRIGGER_NOT_FOUND, TRIGGER_CODE_EXISTS

class TriggerService:
    @classmethod
    def get_all_triggers(cls):
        return NotificationTrigger.objects.prefetch_related("templates").all()

    @classmethod
    def get_trigger_by_id(cls, trigger_id: int):
        try:
            return NotificationTrigger.objects.prefetch_related("templates").get(id=trigger_id)
        except NotificationTrigger.DoesNotExist:
            return None

    @classmethod
    def get_trigger_by_code(cls, code: str):
        try:
            return NotificationTrigger.objects.prefetch_related("templates").get(code=code, is_active=True)
        except NotificationTrigger.DoesNotExist:
            return None

    @classmethod
    def create_trigger(cls, data: dict) -> tuple[bool, str, NotificationTrigger | None]:
        code = data.get("code")
        if NotificationTrigger.objects.filter(code=code).exists():
            return False, TRIGGER_CODE_EXISTS, None
        
        trigger = NotificationTrigger.objects.create(
            name=data.get("name"),
            code=code,
            description=data.get("description", ""),
            event_type=data.get("event_type", "SYSTEM"),
            is_active=data.get("is_active", True)
        )
        return True, "", trigger

    @classmethod
    def update_trigger(cls, trigger_id: int, data: dict) -> tuple[bool, str, NotificationTrigger | None]:
        trigger = cls.get_trigger_by_id(trigger_id)
        if not trigger:
            return False, TRIGGER_NOT_FOUND, None

        if "name" in data:
            trigger.name = data["name"]
        if "description" in data:
            trigger.description = data["description"]
        if "event_type" in data:
            trigger.event_type = data["event_type"]
        if "is_active" in data:
            trigger.is_active = data["is_active"]
        
        trigger.save()
        return True, "", trigger

    @classmethod
    def get_matrix(cls) -> list[dict]:
        triggers = cls.get_all_triggers()
        matrix = []
        channels = [ChannelChoices.WHATSAPP, ChannelChoices.EMAIL, ChannelChoices.WEB_PUSH]

        for trigger in triggers:
            templates_dict = {t.channel: t for t in trigger.templates.all()}
            row = {
                "id": trigger.id,
                "name": trigger.name,
                "code": trigger.code,
                "description": trigger.description,
                "event_type": trigger.event_type,
                "is_active": trigger.is_active,
                "channels": {}
            }
            for ch in channels:
                tmpl = templates_dict.get(ch)
                if tmpl:
                    row["channels"][ch] = {
                        "id": tmpl.id,
                        "name": tmpl.name,
                        "subject": tmpl.subject,
                        "title": tmpl.title,
                        "body": tmpl.body,
                        "whatsapp_template_name": tmpl.whatsapp_template_name,
                        "is_enabled": tmpl.is_enabled,
                        "status": tmpl.status,
                        "variable_mapping": tmpl.variable_mapping,
                        "exists": True
                    }
                else:
                    row["channels"][ch] = {
                        "exists": False,
                        "is_enabled": False,
                        "status": "DRAFT"
                    }
            matrix.append(row)
        return matrix
