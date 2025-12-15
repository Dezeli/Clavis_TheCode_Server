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
    

class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return error_response("refresh_token 값이 필요합니다.")

        try:
            stored = StoredRefreshToken.objects.get(
                token=refresh_token,
                revoked=False,
            )
        except StoredRefreshToken.DoesNotExist:
            return error_response("유효하지 않은 refresh token 입니다.")

        if stored.expires_at < timezone.now():
            return error_response("만료된 refresh token 입니다.")

        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            return error_response("refresh token이 만료되었습니다.")
        except jwt.InvalidTokenError:
            return error_response("손상된 refresh token 입니다.")

        user_id = payload.get("user_id")
        if not user_id:
            return error_response("user_id 가 없는 토큰입니다.")

        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            return error_response("존재하지 않는 사용자입니다.")

        access_payload = {
            "user_id": user.id,
            "exp": timezone.now() + timedelta(minutes=60),
        }
        access_token = jwt.encode(
            access_payload,
            settings.SECRET_KEY,
            algorithm="HS256",
        )

        return success_response(
            message="access token 재발급 성공",
            data={
                "access_token": access_token,
            },
        )
    

class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return error_response("refresh_token 값이 필요합니다.")

        try:
            stored = StoredRefreshToken.objects.get(token=refresh_token)
        except StoredRefreshToken.DoesNotExist:
            return error_response("유효하지 않은 토큰입니다.")

        if stored.revoked:
            return error_response("이미 로그아웃된 상태입니다.")

        stored.revoked = True
        stored.save(update_fields=["revoked"])

        return success_response(message="로그아웃 성공")