from datetime import datetime, timezone as dt_timezone
from django.utils import timezone
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from accounts.models import User, StoredRefreshToken
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from utils.response import success_response, error_response



class GoogleLoginView(APIView):
    permission_classes = []
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

        if decoded.get("iss") not in [
            "accounts.google.com",
            "https://accounts.google.com",
        ]:
            return error_response("잘못된 issuer 입니다.")

        provider_user_id = decoded.get("sub")
        email = decoded.get("email") or ""
        username = decoded.get("name") or ""

        if not provider_user_id:
            return error_response("provider_user_id 없음")

        user, created = User.objects.get_or_create(
            provider="google",
            provider_user_id=provider_user_id,
            defaults={
                "email": email,
                "username": username,
            },
        )

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token


        expires_at_dt = datetime.fromtimestamp(
            int(refresh["exp"]),
            tz=dt_timezone.utc,
        )

        StoredRefreshToken.objects.create(
            user=user,
            token=str(refresh),
            device_info=request.headers.get("User-Agent", ""),
            session_scope="google",
            expires_at=expires_at_dt,
        )

        return success_response(
            message="로그인 성공",
            data={
                "access_token": str(access),
                "refresh_token": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                },
            },
        )
    

class DevTestLoginView(APIView):
    permission_classes = []
    def post(self, request):
        user, _ = User.objects.get_or_create(
            provider="google",
            provider_user_id="dev-google-user-001",
            defaults={
                "email": "dev@test.com",
                "username": "dev_user",
            },
        )

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        expires_at_dt = datetime.fromtimestamp(
            int(refresh["exp"]),
            tz=dt_timezone.utc,
        )
        
        StoredRefreshToken.objects.create(
            user=user,
            token=str(refresh),
            device_info=request.headers.get("User-Agent", ""),
            session_scope="google",
            expires_at=expires_at_dt,
        )


        return success_response(
            message="DEV 테스트 로그인 성공",
            data={
                "access_token": str(access),
                "refresh_token": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                },
            },
        )



class RefreshTokenView(APIView):
    permission_classes = []

    def post(self, request):
        refresh_token_str = request.data.get("refresh_token")
        if not refresh_token_str:
            return error_response("refresh_token 값이 필요합니다.")

        try:
            stored = StoredRefreshToken.objects.get(
                token=refresh_token_str,
                revoked=False,
            )
        except StoredRefreshToken.DoesNotExist:
            return error_response("유효하지 않은 refresh token 입니다.")

        if stored.expires_at < timezone.now():
            return error_response("만료된 refresh token 입니다.")

        try:
            refresh = RefreshToken(refresh_token_str)
        except TokenError:
            return error_response("유효하지 않거나 만료된 refresh token 입니다.")

        access = refresh.access_token

        return success_response(
            message="access token 재발급 성공",
            data={
                "access_token": str(access),
            },
        )
    

class LogoutView(APIView):
    permission_classes = []

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return error_response("refresh_token 값이 필요합니다.")

        try:
            stored = StoredRefreshToken.objects.get(token=refresh_token)
        except StoredRefreshToken.DoesNotExist:
            return error_response("유효하지 않은 토큰입니다.")

        try:
            refresh = RefreshToken(refresh_token)
        except TokenError:
            stored.revoked = True
            stored.save(update_fields=["revoked"])
            return success_response(message="로그아웃 성공")

        if stored.revoked:
            return success_response(message="이미 로그아웃 된 토큰입니다.")

        stored.revoked = True
        stored.save(update_fields=["revoked"])

        return success_response(message="로그아웃 성공")



class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return success_response(
            message="사용자 정보 조회 성공",
            data={
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "provider": user.provider,
                }
            },
        )