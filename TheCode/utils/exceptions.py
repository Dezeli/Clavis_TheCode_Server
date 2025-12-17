from rest_framework.views import exception_handler
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed
from utils.response import error_response


def custom_exception_handler(exc, context):
    if isinstance(exc, NotAuthenticated):
        return error_response("로그인이 필요합니다.", status=401)

    if isinstance(exc, AuthenticationFailed):
        return error_response("인증이 만료되었거나 유효하지 않습니다.", status=401)

    return exception_handler(exc, context)