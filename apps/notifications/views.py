from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.notifications.permissions import IsAdminUserPermission

from apps.notifications.services.trigger_service import TriggerService
from apps.notifications.services.template_service import TemplateService
from apps.notifications.services.delivery_service import DeliveryService
from apps.notifications.serializers import NotificationTriggerSerializer, NotificationTemplateSerializer, NotificationDeliverySerializer
from apps.core.utils import success_response, error_response
from apps.core.constants.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from apps.core.constants.messages import (
    TRIGGER_CREATED_SUCCESS,
    TRIGGER_UPDATED_SUCCESS,
    TEMPLATE_CREATED_SUCCESS,
    TEMPLATE_UPDATED_SUCCESS,
    TEMPLATE_DELETED_SUCCESS,
    TEMPLATE_TOGGLED_SUCCESS,
    TEMPLATE_NOT_FOUND,
    TRIGGER_NOT_FOUND
)

class TriggerListCreateView(APIView):
    permission_classes = [IsAdminUserPermission]

    def get(self, request):
        matrix_mode = request.query_params.get("matrix", "true").lower() in ("true", "1", "t")
        if matrix_mode:
            data = TriggerService.get_matrix()
            return success_response(data=data, status_code=HTTP_200_OK)
        else:
            triggers = TriggerService.get_all_triggers()
            serializer = NotificationTriggerSerializer(triggers, many=True)
            return success_response(data=serializer.data, status_code=HTTP_200_OK)

    def post(self, request):
        success, message, trigger = TriggerService.create_trigger(request.data)
        if not success:
            return error_response(message=message, status_code=HTTP_400_BAD_REQUEST)
        serializer = NotificationTriggerSerializer(trigger)
        return success_response(data=serializer.data, message=TRIGGER_CREATED_SUCCESS, status_code=HTTP_201_CREATED)

class TriggerDetailView(APIView):
    permission_classes = [IsAdminUserPermission]

    def get(self, request, pk):
        trigger = TriggerService.get_trigger_by_id(pk)
        if not trigger:
            return error_response(message=TRIGGER_NOT_FOUND, status_code=HTTP_404_NOT_FOUND)
        serializer = NotificationTriggerSerializer(trigger)
        return success_response(data=serializer.data, status_code=HTTP_200_OK)

    def patch(self, request, pk):
        success, message, trigger = TriggerService.update_trigger(pk, request.data)
        if not success:
            return error_response(message=message, status_code=HTTP_400_BAD_REQUEST)
        serializer = NotificationTriggerSerializer(trigger)
        return success_response(data=serializer.data, message=TRIGGER_UPDATED_SUCCESS, status_code=HTTP_200_OK)

class TemplateListCreateView(APIView):
    permission_classes = [IsAdminUserPermission]

    def get(self, request):
        templates = NotificationTemplate.objects.select_related("trigger").all()
        serializer = NotificationTemplateSerializer(templates, many=True)
        return success_response(data=serializer.data, status_code=HTTP_200_OK)

    def post(self, request):
        success, message, template = TemplateService.create_template(request.data)
        if not success:
            return error_response(message=message, status_code=HTTP_400_BAD_REQUEST)
        serializer = NotificationTemplateSerializer(template)
        return success_response(data=serializer.data, message=TEMPLATE_CREATED_SUCCESS, status_code=HTTP_201_CREATED)

class TemplateDetailView(APIView):
    permission_classes = [IsAdminUserPermission]

    def get(self, request, pk):
        template = TemplateService.get_template_by_id(pk)
        if not template:
            return error_response(message=TEMPLATE_NOT_FOUND, status_code=HTTP_404_NOT_FOUND)
        serializer = NotificationTemplateSerializer(template)
        return success_response(data=serializer.data, status_code=HTTP_200_OK)

    def patch(self, request, pk):
        success, message, template = TemplateService.update_template(pk, request.data)
        if not success:
            return error_response(message=message, status_code=HTTP_400_BAD_REQUEST)
        serializer = NotificationTemplateSerializer(template)
        return success_response(data=serializer.data, message=TEMPLATE_UPDATED_SUCCESS, status_code=HTTP_200_OK)

    def delete(self, request, pk):
        success, message = TemplateService.delete_template(pk)
        if not success:
            return error_response(message=message, status_code=HTTP_404_NOT_FOUND)
        return success_response(message=TEMPLATE_DELETED_SUCCESS, status_code=HTTP_200_OK)

class TemplateToggleView(APIView):
    permission_classes = [IsAdminUserPermission]

    def post(self, request, pk):
        success, message, template = TemplateService.toggle_template(pk)
        if not success:
            return error_response(message=message, status_code=HTTP_400_BAD_REQUEST)
        serializer = NotificationTemplateSerializer(template)
        return success_response(data=serializer.data, message=TEMPLATE_TOGGLED_SUCCESS, status_code=HTTP_200_OK)

class TemplateTestView(APIView):
    permission_classes = [IsAdminUserPermission]

    def post(self, request, pk):
        recipient = request.data.get("recipient")
        test_context = request.data.get("context", {})
        success, message, result_data = TemplateService.test_send_template(pk, recipient, test_context)
        if not success:
            return error_response(message=message, errors=result_data, status_code=HTTP_400_BAD_REQUEST)
        return success_response(data=result_data, message=message, status_code=HTTP_200_OK)

class DeliveryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.query_params.get("user_id")
        if not (request.user.is_staff or request.user.is_superuser):
            user_id = request.user.id
        trigger_code = request.query_params.get("trigger_code")
        status_param = request.query_params.get("status")
        channel = request.query_params.get("channel")

        deliveries = DeliveryService.list_deliveries(
            user_id=user_id,
            trigger_code=trigger_code,
            status=status_param,
            channel=channel
        )
        serializer = NotificationDeliverySerializer(deliveries, many=True)
        return success_response(data=serializer.data, status_code=HTTP_200_OK)


from django.http import HttpResponse
from django.conf import settings
from apps.notifications.models import NotificationDelivery, DeliveryStatusChoices, ChannelChoices

class WhatsAppWebhookView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")

        verify_token = getattr(settings, "WHATSAPP_VERIFY_TOKEN", "starclinch_whatsapp_verify_token")
        if mode == "subscribe" and token == verify_token:
            return HttpResponse(challenge, status=200)
        return HttpResponse("Verification token mismatch", status=403)

    def post(self, request):
        data = request.data
        try:
            entries = data.get("entry", [])
            for entry in entries:
                changes = entry.get("changes", [])
                for change in changes:
                    value = change.get("value", {})
                    statuses = value.get("statuses", [])
                    for st in statuses:
                        wamid = st.get("id")
                        status_str = st.get("status")
                        recipient_id = st.get("recipient_id")
                        errors = st.get("errors", [])

                        delivery = None
                        if wamid:
                            delivery = NotificationDelivery.objects.filter(provider_message_id=wamid).first()
                        if not delivery and recipient_id:
                            delivery = NotificationDelivery.objects.filter(
                                channel=ChannelChoices.WHATSAPP
                            ).order_by("-created_at").first()

                        if delivery:
                            if status_str == "sent":
                                delivery.status = DeliveryStatusChoices.SENT
                            elif status_str in ("delivered", "read"):
                                delivery.status = DeliveryStatusChoices.DELIVERED
                            elif status_str == "failed":
                                delivery.status = DeliveryStatusChoices.FAILED
                                if errors:
                                    delivery.error_message = f"{errors[0].get('title', 'Failed')}: {errors[0].get('message', '')} (Code: {errors[0].get('code')})"
                            delivery.save()
        except Exception as exc:
            pass

        return success_response(message="Webhook processed successfully", status_code=HTTP_200_OK)

