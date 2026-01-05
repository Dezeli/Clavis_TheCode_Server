import base64
import requests
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest
from django.views import View
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_der_public_key

from .models import AdEvent, UserStageHintAccess
from accounts.models import User
from contents.models import Stage

class AdMobSSVView(View):
    KEYS_URL = "https://www.gstatic.com/admob/reward/verifier-keys.json"

    def get(self, request):
        query_string = request.META.get('QUERY_STRING', '')
        user_social_id = request.GET.get('user_id')
        stage_id = request.GET.get('custom_data')
        transaction_id = request.GET.get('transaction_id')
        signature = request.GET.get('signature')
        key_id = request.GET.get('key_id')

        if not all([user_social_id, stage_id, transaction_id, signature, key_id]):
            return HttpResponseBadRequest("Missing parameters")

        if AdEvent.objects.filter(transaction_id=transaction_id).exists():
            return HttpResponse(status=200)

        if not self.verify_signature(query_string, signature, key_id):
            return HttpResponseBadRequest("Invalid signature")

        try:
            with transaction.atomic():
                user = User.objects.get(provider_user_id=user_social_id)
                stage = Stage.objects.get(id=stage_id)

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
        except (User.DoesNotExist, Stage.DoesNotExist):
            return HttpResponseBadRequest("User or Stage not found")
        except Exception as e:
            print(f"Error detail: {e}")
            return HttpResponse(status=500)

    def verify_signature(self, query_string, signature, key_id):
        try:
            keys_res = requests.get(self.KEYS_URL, timeout=5)
            keys = keys_res.json()['keys']
            key_data = next((k for k in keys if str(k['key_id']) == key_id), None)
            if not key_data:
                return False
            message = query_string.split("&signature=")[0].encode('utf-8')
            public_key_der = base64.b64decode(key_data['base64_der'])
            public_key = load_der_public_key(public_key_der)
            sig_bytes = base64.urlsafe_b64decode(signature + '===')
            public_key.verify(sig_bytes, message, ec.ECDSA(hashes.SHA256()))
            return True
        except Exception as e:
            print(f"Signature Verification Failed: {e}")
            return False