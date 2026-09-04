from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.webpush.services.subscription_service import SubscriptionService
from apps.webpush.serializers import WebPushSubscriptionSerializer
from apps.core.utils import success_response, error_response
from apps.core.constants.status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST

class WebPushSubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        success, message, sub = SubscriptionService.subscribe(request.user, request.data)
        if not success:
            return error_response(message=message, status_code=HTTP_400_BAD_REQUEST)
        serializer = WebPushSubscriptionSerializer(sub)
        return success_response(data=serializer.data, message=message, status_code=HTTP_200_OK)
