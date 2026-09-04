from rest_framework import serializers
from apps.notifications.models import NotificationTrigger, NotificationTemplate, NotificationDelivery

class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = [
            "id",
            "trigger",
            "channel",
            "name",
            "subject",
            "title",
            "body",
            "whatsapp_template_name",
            "is_enabled",
            "status",
            "variable_mapping",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "variable_mapping"]

class NotificationTriggerSerializer(serializers.ModelSerializer):
    templates = NotificationTemplateSerializer(many=True, read_only=True)

    class Meta:
        model = NotificationTrigger
        fields = [
            "id",
            "name",
            "code",
            "description",
            "event_type",
            "is_active",
            "created_at",
            "updated_at",
            "templates",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

class NotificationDeliverySerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)
    trigger_code = serializers.CharField(source="trigger.code", read_only=True)
    trigger_name = serializers.CharField(source="trigger.name", read_only=True)

    class Meta:
        model = NotificationDelivery
        fields = [
            "id",
            "user",
            "user_username",
            "trigger",
            "trigger_code",
            "trigger_name",
            "template",
            "channel",
            "status",
            "provider_message_id",
            "error_message",
            "sent_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "sent_at"]
