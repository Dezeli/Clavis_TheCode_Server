import base64
from urllib.parse import unquote

import requests
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest
from django.views import View
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_der_public_key

from .entitlements import serialize_entitlements, user_has_entitlement
from .google_play import GooglePlayPurchaseVerifier, GooglePlayVerificationError
from .models import AdEvent, PurchaseEvent, UserEntitlement, UserStageHintAccess
from .purchase_products import (
    ALL_PRODUCT_IDS,
    ENTITLEMENT_HINT_AD_REMOVAL,
    PRODUCT_ENTITLEMENTS,
)
from accounts.models import User
from contents.models import Stage
from utils.response import error_response, success_response


class EntitlementStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return success_response(
            message="Entitlement status.",
            data=serialize_entitlements(request.user),
        )


class GooglePlayPurchaseVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product_id")
        purchase_token = request.data.get("purchase_token")

        if not product_id or not purchase_token:
            return error_response("product_id and purchase_token are required.", status=400)

        if product_id not in ALL_PRODUCT_IDS:
            return error_response("Unsupported product_id.", status=400)

        try:
            payload = GooglePlayPurchaseVerifier().verify_product_purchase(
                product_id=product_id,
                purchase_token=purchase_token,
            )
        except GooglePlayVerificationError as exc:
            return error_response(str(exc), status=400)

        with transaction.atomic():
            PurchaseEvent.objects.update_or_create(
                purchase_token=purchase_token,
                defaults={
                    "user": request.user,
                    "store": PurchaseEvent.STORE_GOOGLE_PLAY,
                    "product_id": product_id,
                    "order_id": payload.get("orderId"),
                    "payload_json": payload,
                },
            )

            for entitlement_type in PRODUCT_ENTITLEMENTS[product_id]:
                UserEntitlement.objects.get_or_create(
                    user=request.user,
                    entitlement_type=entitlement_type,
                )

        return success_response(
            message="Purchase verified.",
            data=serialize_entitlements(request.user),
        )


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

        has_access = user_has_entitlement(
            request.user,
            ENTITLEMENT_HINT_AD_REMOVAL,
        ) or UserStageHintAccess.objects.filter(user=request.user, stage=stage).exists()

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
                unquote(message).encode("utf-8"),
                ec.ECDSA(hashes.SHA256()),
            )
            return True
        except Exception as e:
            print(f"Signature Verification Failed: {e}")
            return False
