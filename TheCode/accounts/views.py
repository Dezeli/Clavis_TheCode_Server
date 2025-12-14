import jwt
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from rest_framework.views import APIView

from accounts.models import User, StoredRefreshToken
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from utils.response import success_response, error_response



class GoogleLoginView(APIView):
    def post(self, request):
        token = request.data.get("id_token")
        if not token:
            return error_response("id_token 값이 필요합니다.")

        try:
            decoded = google_id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_AUTH_CLIENT_ID,
            )
        except Exception as e:
            return error_response(
                "유효하지 않은 Google ID Token 입니다.",
                data={"detail": str(e)},
            )

        if decoded.get("iss") not in ["accounts.google.com", "https://accounts.google.com"]:
            return error_response("잘못된 issuer 입니다.")

        provider_user_id = decoded.get("sub")
        email = decoded.get("email") or ""
        username = decoded.get("name") or ""

        if not provider_user_id:
            return error_response("provider_user_id 없음")

        user, created = User.objects.get_or_create(
            provider="google",
            provider_user_id=provider_user_id,
            defaults={"email": email, "username": username},
        )

        access_payload = {
            "user_id": user.id,
            "exp": timezone.now() + timedelta(minutes=60),
        }
        access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm="HS256")

        refresh_payload = {
            "user_id": user.id,
            "exp": timezone.now() + timedelta(days=7),
        }
        refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm="HS256")

        StoredRefreshToken.objects.create(
            user=user,
            token=refresh_token,
            device_info=request.headers.get("User-Agent", ""),
            session_scope="google",
            expires_at=timezone.now() + timedelta(days=7),
        )

        return success_response(
            message="로그인 성공",
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                },
            },
        )