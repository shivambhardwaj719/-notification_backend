import time
import requests
from django.conf import settings
from django.core.mail import EmailMessage
from apps.notifications.services.base_provider import BaseNotificationService

class EmailService(BaseNotificationService):
    def send(self, recipient: str, content: str, subject: str = None, title: str = None, context: dict = None) -> dict:
        host_user = getattr(settings, "EMAIL_HOST_USER", "")
        host_password = getattr(settings, "EMAIL_HOST_PASSWORD", "")
        postmark_token = getattr(settings, "POSTMARKAPP_TOKEN", "")
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "notifications@example.com")
        email_subject = subject or "Notification Alert"

        if host_user and host_password:
            try:
                msg = EmailMessage(
                    subject=email_subject,
                    body=content,
                    from_email=from_email or host_user,
                    to=[recipient],
                )
                msg.content_subtype = "html"
                msg.send(fail_silently=False)
                return {
                    "success": True,
                    "provider_message_id": f"smtp_gmail_{int(time.time()*1000)}",
                    "error_message": None
                }
            except Exception as exc:
                return {
                    "success": False,
                    "provider_message_id": None,
                    "error_message": str(exc)
                }

        if postmark_token:
            url = "https://api.postmarkapp.com/email"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Postmark-Server-Token": postmark_token,
            }
            payload = {
                "From": getattr(settings, "POSTMARK_FROM_EMAIL", from_email),
                "To": recipient,
                "Subject": email_subject,
                "TextBody": content,
                "HtmlBody": f"<p>{content}</p>",
                "MessageStream": "outbound"
            }

            try:
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    msg_id = data.get("MessageID", f"pm_{int(time.time())}")
                    return {"success": True, "provider_message_id": str(msg_id), "error_message": None}
                else:
                    return {"success": False, "provider_message_id": None, "error_message": response.text}
            except Exception as exc:
                return {"success": False, "provider_message_id": None, "error_message": str(exc)}

        return {
            "success": True,
            "provider_message_id": f"mock_email_{int(time.time()*1000)}",
            "error_message": None
        }
