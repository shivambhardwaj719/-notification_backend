from rest_framework.response import Response
from apps.core.constants.status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST

def api_response(data=None, message=None, status_code=HTTP_200_OK, success=True, errors=None):
    payload = {
        "success": success,
        "message": message,
        "data": data,
        "errors": errors
    }
    return Response(payload, status=status_code)

def success_response(data=None, message=None, status_code=HTTP_200_OK):
    return api_response(data=data, message=message, status_code=status_code, success=True)

def error_response(message=None, errors=None, status_code=HTTP_400_BAD_REQUEST):
    return api_response(data=None, message=message, status_code=status_code, success=False, errors=errors)
