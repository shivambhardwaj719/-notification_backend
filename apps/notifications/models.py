from django.db import models
from django.conf import settings

class ChannelChoices(models.TextChoices):
    WHATSAPP = "WHATSAPP", "WhatsApp"
    EMAIL = "EMAIL", "Email"
    WEB_PUSH = "WEB_PUSH", "Web Push"

class StatusChoices(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    ACTIVE = "ACTIVE", "Active"
    DISABLED = "DISABLED", "Disabled"
    FAILED = "FAILED", "Failed"

class DeliveryStatusChoices(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SENT = "SENT", "Sent"
    FAILED = "FAILED", "Failed"
    SKIPPED = "SKIPPED", "Skipped"

class NotificationTrigger(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True, default="")
    event_type = models.CharField(max_length=50, default="SYSTEM")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notification_triggers"
        ordering = ["code"]

    def __str__(self):
        return f"{self.name} ({self.code})"

class NotificationTemplate(models.Model):
    trigger = models.ForeignKey(NotificationTrigger, on_delete=models.CASCADE, related_name="templates")
    channel = models.CharField(max_length=20, choices=ChannelChoices.choices)
    name = models.CharField(max_length=150)
    subject = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    body = models.TextField()
    whatsapp_template_name = models.CharField(max_length=100, blank=True, null=True)
    is_enabled = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    variable_mapping = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notification_templates"
        constraints = [
            models.UniqueConstraint(fields=["trigger", "channel"], name="unique_trigger_channel_template")
        ]
        indexes = [
            models.Index(fields=["trigger", "channel"]),
        ]

    def __str__(self):
        return f"{self.trigger.code} - {self.channel} ({self.name})"

class NotificationDelivery(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="deliveries")
    trigger = models.ForeignKey(NotificationTrigger, on_delete=models.CASCADE, related_name="deliveries")
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name="deliveries")
    channel = models.CharField(max_length=20, choices=ChannelChoices.choices)
    status = models.CharField(max_length=20, choices=DeliveryStatusChoices.choices, default=DeliveryStatusChoices.PENDING)
    provider_message_id = models.CharField(max_length=255, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "notification_deliveries"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["trigger"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Delivery #{self.id} [{self.channel}] - {self.status}"
