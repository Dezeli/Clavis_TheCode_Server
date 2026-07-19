import base64
import requests
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest
from django.views import View
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_der_public_key

from .models import AdEvent, UserStageHintAccess
from accounts.models import User
from contents.models import Stage
from utils.response import error_response, success_response


class HintAccessStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, episode_id, stage_no):
        try:
            stage = Stage.objects.select_related("episode").get(
                episode_id=episode_id,
                stage_no=stage_no,
            )
        except Stage.DoesNotExist:
            return error_response("Stage does not exist.", status=404)

        has_access = UserStageHintAccess.objects.filter(
            user=request.user,
            stage=stage,
        ).exists()

        return success_response(
            message="Hint access status.",
            data={
                "episode_id": stage.episode_id,
                "episode_code": stage.episode.code,
                "stage_no": stage.stage_no,
                "has_access": has_access,
            },
        )

class AdMobSSVView(View):
    KEYS_URL = "https://www.gstatic.com/admob/reward/verifier-keys.json"

    def get(self, request):
        query_string = request.META.get('QUERY_STRING', '')
        user_social_id = request.GET.get('user_id')
        custom_data_raw = request.GET.get('custom_data')
        transaction_id = request.GET.get('transaction_id')
        signature = request.GET.get('signature')
        key_id = request.GET.get('key_id')

        if not all([user_social_id, custom_data_raw, transaction_id, signature, key_id]):
            return HttpResponseBadRequest("Missing parameters")

        if AdEvent.objects.filter(transaction_id=transaction_id).exists():
            return HttpResponse(status=200)

        if not self.verify_signature(query_string, signature, key_id):
            return HttpResponseBadRequest("Invalid signature")

        try:
            try:
                ep_code, s_no = custom_data_raw.split('|')
            except ValueError:
                return HttpResponseBadRequest("Invalid custom_data format. Expected 'EP_CODE|STAGE_NO'")

            with transaction.atomic():
                user = User.objects.get(provider_user_id=user_social_id)
                stage = Stage.objects.get(
                    episode__code=ep_code, 
                    stage_no=s_no
                )

                ad_event = AdEvent.objects.create(
                    user=user,
                    stage=stage,
                    transaction_id=transaction_id
                )

                UserStageHintAccess.objects.get_or_create(
                    user=user,
                    stage=stage,
                    defaults={
                        'ad_event': ad_event,
                    }
                )
            
            return HttpResponse(status=200)

        except User.DoesNotExist:
            return HttpResponseBadRequest("User not found")
        except Stage.DoesNotExist:
            return HttpResponseBadRequest("Stage not found")
        except Exception as e:
            print(f"Error detail: {e}")
            return HttpResponse(status=500)
        

    def verify_signature(self, query_string, signature, key_id):
        try:
            signature_marker = "&signature="
            key_id_marker = "&key_id="
            if signature_marker not in query_string:
                return False

            message, signature_and_key = query_string.split(signature_marker, 1)
            if key_id_marker not in signature_and_key:
                return False

            raw_signature, raw_key_id = signature_and_key.split(key_id_marker, 1)
            if "&" in raw_key_id:
                return False

            if raw_signature != signature or raw_key_id != key_id:
                return False

            keys_res = requests.get(self.KEYS_URL, timeout=5)
            keys_res.raise_for_status()
            keys = keys_res.json()['keys']
            key_data = next((k for k in keys if str(k['keyId']) == key_id), None)
            if not key_data:
                return False

            public_key_der = base64.b64decode(key_data['base64'])
            public_key = load_der_public_key(public_key_der)
            padding = "=" * (-len(raw_signature) % 4)
            sig_bytes = base64.urlsafe_b64decode(raw_signature + padding)
            public_key.verify(
                sig_bytes,
                message.encode("utf-8"),
                ec.ECDSA(hashes.SHA256()),
            )
            return True
        except Exception as e:
            print(f"Signature Verification Failed: {e}")
            return False
