from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.notifications.models import NotificationTrigger, NotificationTemplate, ChannelChoices, StatusChoices

User = get_user_model()

class Command(BaseCommand):
    help = "Seeds database with default triggers, templates, admin, and test users."

    def handle(self, *args, **options):
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "shivambhardwaj719@gmail.com",
                "phone": "+916376082733",
                "is_staff": True,
                "is_superuser": True
            }
        )
        admin_user.email = "shivambhardwaj719@gmail.com"
        admin_user.phone = "+916376082733"
        admin_user.set_password("admin123")
        admin_user.save()

        normal_user, _ = User.objects.get_or_create(
            username="user",
            defaults={
                "email": "shivambhardwaj719@gmail.com",
                "phone": "+916376082733",
                "is_staff": False,
                "is_superuser": False
            }
        )
        normal_user.email = "shivambhardwaj719@gmail.com"
        normal_user.phone = "+916376082733"
        normal_user.set_password("user123")
        normal_user.save()

        triggers_data = [
            {
                "code": "LOGIN",
                "name": "User Login",
                "description": "Triggered when a user successfully logs into the platform.",
                "event_type": "AUTHENTICATION"
            },
            {
                "code": "LOGOUT",
                "name": "User Logout",
                "description": "Triggered when a user logs out of their account session.",
                "event_type": "AUTHENTICATION"
            },
            {
                "code": "PASSWORD_RESET",
                "name": "Password Reset",
                "description": "Triggered when a password reset is requested.",
                "event_type": "SECURITY"
            },
            {
                "code": "ORDER_PLACED",
                "name": "Order Placed",
                "description": "Triggered when a new order is completed.",
                "event_type": "TRANSACTIONAL"
            },
            {
                "code": "INACTIVE_1_DAY",
                "name": "Inactive for 1 Day",
                "description": "Triggered when user is inactive for 24 hours.",
                "event_type": "ENGAGEMENT"
            },
            {
                "code": "INACTIVE_1_WEEK",
                "name": "Inactive for 1 Week",
                "description": "Triggered when user is inactive for 7 consecutive days.",
                "event_type": "ENGAGEMENT"
            },
        ]

        triggers_dict = {}
        for item in triggers_data:
            t, _ = NotificationTrigger.objects.get_or_create(
                code=item["code"],
                defaults={
                    "name": item["name"],
                    "description": item["description"],
                    "event_type": item["event_type"],
                    "is_active": True
                }
            )
            triggers_dict[item["code"]] = t

        login_trigger = triggers_dict["LOGIN"]
        NotificationTemplate.objects.get_or_create(
            trigger=login_trigger,
            channel=ChannelChoices.WHATSAPP,
            defaults={
                "name": "Login WhatsApp Alert",
                "body": "Welcome back {{user_name}}! You logged in at {{login_time}}.",
                "whatsapp_template_name": "welcome_back_alert",
                "is_enabled": True,
                "status": StatusChoices.ACTIVE,
                "variable_mapping": {"vars": ["user_name", "login_time"]}
            }
        )
        NotificationTemplate.objects.get_or_create(
            trigger=login_trigger,
            channel=ChannelChoices.EMAIL,
            defaults={
                "name": "Login Email Notification",
                "subject": "Successful Login Notification",
                "body": "Hello {{user_name}},\n\nYou successfully logged in to {{site_name}} at {{login_time}}.",
                "is_enabled": True,
                "status": StatusChoices.ACTIVE,
                "variable_mapping": {"vars": ["user_name", "site_name", "login_time"]}
            }
        )
        NotificationTemplate.objects.get_or_create(
            trigger=login_trigger,
            channel=ChannelChoices.WEB_PUSH,
            defaults={
                "name": "Login Web Push Notification",
                "title": "Welcome Back!",
                "body": "Welcome back {{user_name}}! Account login detected.",
                "is_enabled": True,
                "status": StatusChoices.ACTIVE,
                "variable_mapping": {"vars": ["user_name"]}
            }
        )

        logout_trigger = triggers_dict["LOGOUT"]
        NotificationTemplate.objects.get_or_create(
            trigger=logout_trigger,
            channel=ChannelChoices.WHATSAPP,
            defaults={
                "name": "Logout WhatsApp Notice",
                "body": "Goodbye {{user_name}}, you logged out at {{logout_time}}.",
                "whatsapp_template_name": "logout_notice",
                "is_enabled": True,
                "status": StatusChoices.ACTIVE,
                "variable_mapping": {"vars": ["user_name", "logout_time"]}
            }
        )
        NotificationTemplate.objects.get_or_create(
            trigger=logout_trigger,
            channel=ChannelChoices.EMAIL,
            defaults={
                "name": "Logout Email Confirmation",
                "subject": "Logout Confirmation",
                "body": "Hello {{user_name}},\n\nYou have logged out at {{logout_time}}.",
                "is_enabled": True,
                "status": StatusChoices.ACTIVE,
                "variable_mapping": {"vars": ["user_name", "logout_time"]}
            }
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded triggers, templates, and users."))
