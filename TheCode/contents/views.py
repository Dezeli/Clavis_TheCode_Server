import boto3
from django.http import StreamingHttpResponse, Http404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

from contents.models import Stage

class StageImageProxyView(APIView):
    permission_classes = []
    # permission_classes = [IsAuthenticated]

    def get(self, request, stage_id):
        try:
            stage = Stage.objects.get(id=stage_id)
        except Stage.DoesNotExist:
            raise Http404

        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )

        obj = s3.get_object(
            Bucket=settings.AWS_STAGE_BUCKET,
            Key=stage.image_key,
        )

        response = StreamingHttpResponse(
            obj["Body"].iter_chunks(8192),
            content_type=obj.get("ContentType", "image/png"),
        )

        response["Content-Length"] = obj["ContentLength"]
        response["Cache-Control"] = "no-store"

        return response