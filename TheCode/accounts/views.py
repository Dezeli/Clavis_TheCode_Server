import jwt
import requests
import urllib.parse
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from rest_framework.views import APIView

from accounts.models import User, StoredRefreshToken
from utils.response import success_response, error_response


class GoogleLoginURLView(APIView):
    def get(self, request):

        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_REDIRECT_URI:
            return error_response(
                "Google OAuth 설정값이 올바르지 않습니다. (client_id 또는 redirect_uri 없음)"
            )

        base_url = "https://accounts.google.com/o/oauth2/v2/auth"

        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent"
        }

        login_url = f"{base_url}?{urllib.parse.urlencode(params)}"

        return success_response(
            message="Google 로그인 URL 생성 완료",
            data={"login_url": login_url}
        )


class GoogleAuthCallbackView(APIView):
    def post(self, request):
        code = request.data.get("code")

        if not code:
            return error_response("code 값이 필요합니다.")

        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        token_res = requests.post(token_url, data=data)
        token_data = token_res.json()

        if "id_token" not in token_data:
            return error_response(
                "Google로부터 토큰을 가져오지 못했습니다.",
                data={"detail": token_data}
            )

        id_token = token_data["id_token"]

        try:
            decoded = jwt.decode(id_token, options={"verify_signature": False})
        except Exception:
            return error_response("ID Token 디코딩 실패")

        provider_user_id = decoded.get("sub")
        email = decoded.get("email")
        username = decoded.get("name")

        if not provider_user_id:
            return error_response("provider_user_id 없음")

        user, created = User.objects.get_or_create(
            provider="google",
            provider_user_id=provider_user_id,
            defaults={"email": email, "username": username}
        )

        access_payload = {
            "user_id": user.id,
            "exp": timezone.now() + timedelta(minutes=60)
        }

        access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm="HS256")

        refresh_payload = {
            "user_id": user.id,
            "exp": timezone.now() + timedelta(days=7)
        }

        refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm="HS256")

        StoredRefreshToken.objects.create(
            user=user,
            token=refresh_token,
            device_info=request.headers.get("User-Agent", ""),
            session_scope="user",
            expires_at=timezone.now() + timedelta(days=7)
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
                }
            }
        )



from django.http import HttpResponse

class GoogleTestRedirectView(APIView):
    def get(self, request):
        code = request.GET.get("code")
        error = request.GET.get("error")

        if error:
            return HttpResponse(f"Google OAuth Error: {error}")

        if not code:
            return HttpResponse("No code parameter received.")

        # 화면에 code 보여주기
        return HttpResponse(f"""
            <h2>Google OAuth Code Received!</h2>
            <p>아래 코드를 Postman에서 callback API 테스트에 사용하세요.</p>
            <pre style="padding: 10px; background: #eee; border-radius: 4px;">
{code}
            </pre>
        """)