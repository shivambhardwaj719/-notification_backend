from datetime import datetime
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from apps.notifications.services.notification_service import NotificationService
from apps.core.constants.messages import INVALID_CREDENTIALS, LOGIN_SUCCESS, LOGOUT_SUCCESS

class AuthService:
    @classmethod
    def login(cls, username: str, password: str) -> tuple[bool, str, dict]:
        user = authenticate(username=username, password=password)
        if not user:
            return False, INVALID_CREDENTIALS, {}

        refresh = RefreshToken.for_user(user)
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser
        }

        login_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        try:
            NotificationService.trigger(
                trigger_code="LOGIN",
                user=user,
                context={
                    "user_name": user.get_full_name() or user.username,
                    "user_email": user.email or "",
                    "login_time": login_time,
                    "site_name": "Notification System"
                }
            )
        except Exception as exc:
            pass

        return True, LOGIN_SUCCESS, {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": user_data
        }

    @classmethod
    def logout(cls, user) -> tuple[bool, str]:
        if user and user.is_authenticated:
            logout_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            try:
                NotificationService.trigger(
                    trigger_code="LOGOUT",
                    user=user,
                    context={
                        "user_name": user.get_full_name() or user.username,
                        "user_email": user.email or "",
                        "logout_time": logout_time,
                        "site_name": "Notification System"
                    }
                )
            except Exception:
                pass
        return True, LOGOUT_SUCCESS

