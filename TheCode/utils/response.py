from rest_framework.response import Response


def success_response(message="요청이 성공적으로 처리되었습니다.", data=None, status=200):
    return Response({
        "success": True,
        "data": {
            "message": message,
            **(data or {})
        }
    }, status=status)


def error_response(message="요청 처리에 실패했습니다.", data=None, status=400):
    return Response({
        "success": False,
        "data": {
            "message": message,
            **(data or {})
        }
    }, status=status)
