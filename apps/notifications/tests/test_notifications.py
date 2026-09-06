import os

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.notifications.models import NotificationTrigger, NotificationTemplate, NotificationDelivery, ChannelChoices, StatusChoices
from apps.notifications.services.trigger_service import TriggerService
from apps.notifications.services.template_service import TemplateService
from apps.notifications.services.variable_service import VariableService
from apps.notifications.services.webpush_service import WebPushService, _resolve_firebase_credential_path
from apps.authentication.services.auth_service import AuthService

User = get_user_model()

class NotificationSystemTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin_test",
            email="admin@test.com",
            password="adminpassword123"
        )
        self.user = User.objects.create_user(
            username="user_test",
            email="user@test.com",
            password="userpassword123",
            phone="+111222333"
        )

        self.login_trigger = NotificationTrigger.objects.create(
            name="Login Trigger",
            code="LOGIN",
            description="Login Description",
            event_type="AUTHENTICATION",
            is_active=True
        )

        self.trigger = NotificationTrigger.objects.create(
            name="Test Trigger",
            code="TEST_EVENT",
            description="Test Description",
            event_type="TEST",
            is_active=True
        )

        self.template = NotificationTemplate.objects.create(
            trigger=self.trigger,
            channel=ChannelChoices.EMAIL,
            name="Email Test Template",
            subject="Hello {{user_name}}",
            body="Welcome {{user_name}} to {{site_name}}",
            is_enabled=True,
            status=StatusChoices.ACTIVE
        )

        self.client = APIClient()

    def test_variable_rendering(self):
        body = "Hello {{user_name}}, your order {{order_id}} is ready."
        ctx = {"user_name": "Alice", "order_id": "ORD-99"}
        rendered = VariableService.render_template(body, ctx)
        self.assertEqual(rendered, "Hello Alice, your order ORD-99 is ready.")

    def test_trigger_matrix_service(self):
        matrix = TriggerService.get_matrix()
        self.assertGreaterEqual(len(matrix), 1)
        test_row = next(item for item in matrix if item["code"] == "TEST_EVENT")
        self.assertTrue(test_row["channels"][ChannelChoices.EMAIL]["exists"])
        self.assertFalse(test_row["channels"][ChannelChoices.WHATSAPP]["exists"])

    def test_template_unique_constraint(self):
        success, message, tmpl = TemplateService.create_template({
            "trigger_id": self.trigger.id,
            "channel": ChannelChoices.EMAIL,
            "name": "Duplicate Email Template",
            "body": "Duplicate Body"
        })
        self.assertFalse(success)

    def test_template_toggle(self):
        success, message, tmpl = TemplateService.toggle_template(self.template.id)
        self.assertTrue(success)
        self.assertFalse(tmpl.is_enabled)
        self.assertEqual(tmpl.status, StatusChoices.DISABLED)

    def test_auth_login_trigger_firing(self):
        success, message, data = AuthService.login("user_test", "userpassword123")
        self.assertTrue(success)
        deliveries = NotificationDelivery.objects.filter(user=self.user)
        self.assertGreaterEqual(deliveries.count(), 1)

    def test_test_send_template(self):
        success, message, res = TemplateService.test_send_template(
            template_id=self.template.id,
            recipient="test@example.com"
        )
        self.assertTrue(success)
        self.assertIn("delivery_id", res)

    def test_webpush_credential_resolution(self):
        resolved_path = _resolve_firebase_credential_path()
        self.assertTrue(resolved_path)
        self.assertTrue(os.path.exists(resolved_path))
        self.assertTrue(resolved_path.endswith("config/firebase-credentials.json"))

        service = WebPushService()
        response = service.send(recipient="fcm-token-long-enough-for-test-1234567890", content="hello")
        self.assertTrue(response["success"])

    def test_admin_permissions(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/notifications/triggers/")
        self.assertEqual(response.status_code, 403)

        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/notifications/triggers/")
        self.assertEqual(response.status_code, 200)
