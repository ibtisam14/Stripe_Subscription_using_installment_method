from rest_framework.response import Response

def success_response(message, data=None, status_code=200):
    """
    Returns a uniform success response.
    """
    return Response({
        "status_code": status_code,
        "status": "success",
        "message": message,
        "data": data or {}
    }, status=status_code)


def error_response(message, status_code=400, data=None):
    """
    Returns a uniform error response.
    """
    return Response({
        "status_code": status_code,
        "status": "error",
        "message": message,
        "data": data or {}
    }, status=status_code)
