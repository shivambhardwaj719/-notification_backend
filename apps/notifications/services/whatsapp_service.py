import os
import time
import requests
from django.conf import settings
from apps.notifications.services.base_provider import BaseNotificationService

class WhatsAppService(BaseNotificationService):
    def send(self, recipient: str, content: str, subject: str = None, title: str = None, context: dict = None) -> dict:
        access_token = os.getenv("WHATSAPP_ACCESS_TOKEN") or getattr(settings, "WHATSAPP_ACCESS_TOKEN", "")
        phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID") or getattr(settings, "WHATSAPP_PHONE_NUMBER_ID", "")
        version = os.getenv("WHATSAPP_API_VERSION") or getattr(settings, "WHATSAPP_API_VERSION", "v18.0")

        if not access_token or not phone_number_id:
            return {
                "success": True,
                "provider_message_id": f"wa_sandbox_mock_{int(time.time()*1000)}",
                "error_message": None
            }

        url = f"https://graph.facebook.com/{version}/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        clean_recipient = recipient.replace("+", "").replace(" ", "")

        payload = {
            "messaging_product": "whatsapp",
            "to": clean_recipient,
            "type": "template",
            "template": {
                "name": "hello_world",
                "language": {"code": "en_US"}
            }
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code in (200, 201):
                data = response.json()
                msg_id = data.get("messages", [{}])[0].get("id", f"wa_{int(time.time())}")
                return {"success": True, "provider_message_id": msg_id, "error_message": None}
            else:
                text_payload = {
                    "messaging_product": "whatsapp",
                    "to": clean_recipient,
                    "type": "text",
                    "text": {"body": content}
                }
                res2 = requests.post(url, json=text_payload, headers=headers, timeout=10)
                if res2.status_code in (200, 201):
                    d2 = res2.json()
                    msg_id2 = d2.get("messages", [{}])[0].get("id", f"wa_{int(time.time())}")
                    return {"success": True, "provider_message_id": msg_id2, "error_message": None}
                return {"success": False, "provider_message_id": None, "error_message": response.text}
        except Exception as exc:
            return {"success": False, "provider_message_id": None, "error_message": str(exc)}
