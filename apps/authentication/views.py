from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from apps.authentication.serializers import LoginSerializer, UserSerializer
from apps.authentication.services.auth_service import AuthService
from apps.core.utils import success_response, error_response
from apps.core.constants.status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="Invalid input data.", errors=serializer.errors, status_code=HTTP_400_BAD_REQUEST)

        success, message, data = AuthService.login(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"]
        )
        if not success:
            return error_response(message=message, status_code=HTTP_400_BAD_REQUEST)
        return success_response(data=data, message=message, status_code=HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        success, message = AuthService.logout(request.user)
        return success_response(message=message, status_code=HTTP_200_OK)

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return success_response(data=serializer.data, status_code=HTTP_200_OK)
