import os
import time
import requests
from django.conf import settings
from apps.notifications.services.base_provider import BaseNotificationService

class WebPushService(BaseNotificationService):
    def send(self, recipient: str, content: str, subject: str = None, title: str = None, context: dict = None) -> dict:
        app_id = os.getenv("ONESIGNAL_APP_ID") or getattr(settings, "ONESIGNAL_APP_ID", "")
        api_key = os.getenv("ONESIGNAL_REST_API_KEY") or getattr(settings, "ONESIGNAL_REST_API_KEY", "")

        if not app_id or not api_key or api_key == "mock_onesignal_key" or app_id == "00000000-0000-0000-0000-000000000000":
            return {
                "success": True,
                "provider_message_id": f"onesignal_mock_{int(time.time()*1000)}",
                "error_message": None
            }

        url = "https://onesignal.com/api/v1/notifications"
        headers = {
            "Authorization": f"Basic {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "app_id": app_id,
            "include_player_ids": [recipient] if recipient else [],
            "headings": {"en": title or "Notification Alert"},
            "contents": {"en": content},
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                msg_id = data.get("id", f"os_{int(time.time())}")
                return {"success": True, "provider_message_id": str(msg_id), "error_message": None}
            else:
                return {"success": False, "provider_message_id": None, "error_message": response.text}
        except Exception as exc:
            return {"success": False, "provider_message_id": None, "error_message": str(exc)}
