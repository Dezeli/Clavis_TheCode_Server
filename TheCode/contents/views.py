from urllib.parse import urljoin

from commerce.models import UserStageHintAccess
from commerce.entitlements import user_has_entitlement
from commerce.purchase_products import ENTITLEMENT_HINT_AD_REMOVAL
from contents.models import Episode, Hint, Stage
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from utils.response import success_response, error_response
from utils.s3 import get_s3_client


def build_stage_image_url(request, image_key):
    if not image_key:
        return None

    if image_key.startswith("http://") or image_key.startswith("https://"):
        return image_key

    if settings.MEDIA_URL and not image_key.startswith("s3://"):
        return request.build_absolute_uri(urljoin(settings.MEDIA_URL, image_key))

    s3 = get_s3_client()
    if not s3 or not settings.AWS_STAGE_BUCKET:
        return None

    key = image_key.removeprefix("s3://")
    if "/" in key and key.split("/", 1)[0] == settings.AWS_STAGE_BUCKET:
        key = key.split("/", 1)[1]

    return s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": settings.AWS_STAGE_BUCKET,
            "Key": key,
        },
        ExpiresIn=60,
    )


class StartStageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        episode = (
            Episode.objects.filter(
                is_released=True,
                series__is_active=True,
                stages__isnull=False,
            )
            .select_related("series")
            .order_by("series__code", "code", "id")
            .distinct()
            .first()
        )

        if not episode:
            return error_response("Released episode does not exist.", status=404)

        stage = episode.stages.order_by("stage_no").first()
        if not stage:
            return error_response("Start stage does not exist.", status=404)

        return success_response(
            message="Start stage information.",
            data={
                "episode_id": episode.id,
                "episode_code": episode.code,
                "stage_no": stage.stage_no,
            },
        )


class StageDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, episode_id, stage_no):
        try:
            stage = Stage.objects.select_related("episode").get(
                episode_id=episode_id,
                stage_no=stage_no,
            )
        except Stage.DoesNotExist:
            return error_response("스테이지가 존재하지 않습니다.", status=404)

        next_stage = (
            Stage.objects.filter(
                episode_id=episode_id,
                stage_no__gt=stage.stage_no,
            )
            .order_by("stage_no")
            .first()
        )

        next_stage_no = next_stage.stage_no if next_stage else None

        image_url = build_stage_image_url(request, stage.image_key)

        return success_response(
            message="스테이지 정보입니다.",
            data={
                "episode_id": stage.episode_id,
                "episode_code": stage.episode.code,
                "stage_no": stage.stage_no,
                "title": stage.title,
                "image_url": image_url,
                "next_stage_no": next_stage_no,
            },
        )
    

def normalize_answer(answer: str) -> str:
    return answer.strip().lower()

class StageAnswerView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, episode_id, stage_no):
        answer = request.data.get("answer")
        if not answer:
            return error_response("answer 값이 필요합니다.", status=400)

        try:
            stage = Stage.objects.get(
                episode_id=episode_id,
                stage_no=stage_no,
            )
        except Stage.DoesNotExist:
            return error_response("스테이지가 존재하지 않습니다.", status=404)

        is_correct = normalize_answer(answer) == normalize_answer(stage.answer_text)

        if is_correct:
            return success_response(
                message="정답입니다.",
                data={"is_correct": True},
            )
        else:
            return success_response(
                message="오답입니다.",
                data={"is_correct": False},
            )
        

class StageHintView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, episode_id, stage_no):
        try:
            stage = Stage.objects.get(
                episode_id=episode_id,
                stage_no=stage_no,
            )
        except Stage.DoesNotExist:
            return error_response("스테이지가 존재하지 않습니다.", status=404)

        try:
            hint = stage.hint
        except Hint.DoesNotExist:
            return error_response("해당 문제에는 힌트가 없습니다.", status=404)

        if not user_has_entitlement(
            request.user,
            ENTITLEMENT_HINT_AD_REMOVAL,
        ) and not UserStageHintAccess.objects.filter(
            user=request.user,
            stage=stage,
        ).exists():
            return error_response("Hint access requires a rewarded ad.", status=403)

        return success_response(
            message="힌트 정보입니다.",
            data={
                "content": hint.content,
            },
        )
