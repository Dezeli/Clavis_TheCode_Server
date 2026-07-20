import json
from pathlib import Path

from django.conf import settings
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account


class GooglePlayVerificationError(Exception):
    pass


class GooglePlayPurchaseVerifier:
    scopes = ["https://www.googleapis.com/auth/androidpublisher"]

    def __init__(self):
        self.package_name = getattr(settings, "GOOGLE_PLAY_PACKAGE_NAME", "")
        self.service_account_file = getattr(
            settings,
            "GOOGLE_PLAY_SERVICE_ACCOUNT_FILE",
            "",
        )
        self.service_account_json = getattr(
            settings,
            "GOOGLE_PLAY_SERVICE_ACCOUNT_JSON",
            "",
        )

    def verify_product_purchase(self, product_id, purchase_token):
        if not self.package_name:
            raise GooglePlayVerificationError("GOOGLE_PLAY_PACKAGE_NAME is not configured.")

        session = self._create_session()
        url = (
            "https://androidpublisher.googleapis.com/androidpublisher/v3/"
            f"applications/{self.package_name}/purchases/products/"
            f"{product_id}/tokens/{purchase_token}"
        )
        response = session.get(url, timeout=10)
        if response.status_code >= 400:
            raise GooglePlayVerificationError(
                f"Google Play verification failed ({response.status_code})."
            )

        payload = response.json()
        if payload.get("purchaseState") != 0:
            raise GooglePlayVerificationError("Purchase is not completed.")

        if payload.get("acknowledgementState") == 0:
            ack_response = session.post(f"{url}:acknowledge", json={}, timeout=10)
            if ack_response.status_code >= 400:
                raise GooglePlayVerificationError(
                    f"Google Play acknowledge failed ({ack_response.status_code})."
                )

        return payload

    def _create_session(self):
        if self.service_account_json:
            credentials_info = json.loads(self.service_account_json)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=self.scopes,
            )
            return AuthorizedSession(credentials)

        if self.service_account_file:
            path = Path(self.service_account_file)
            if not path.exists():
                raise GooglePlayVerificationError(
                    "GOOGLE_PLAY_SERVICE_ACCOUNT_FILE does not exist."
                )
            credentials = service_account.Credentials.from_service_account_file(
                path,
                scopes=self.scopes,
            )
            return AuthorizedSession(credentials)

        raise GooglePlayVerificationError(
            "Google Play service account credentials are not configured."
        )
