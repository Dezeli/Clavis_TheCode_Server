import boto3
from django.conf import settings

def get_s3_client():
    if not all([
        settings.AWS_ACCESS_KEY_ID,
        settings.AWS_SECRET_ACCESS_KEY,
        settings.AWS_REGION,
    ]):
        return None

    return boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )
