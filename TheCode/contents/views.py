from contents.models import Hint, Stage
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from utils.response import success_response, error_response
from utils.s3 import get_s3_client


s3 = get_s3_client()


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

        image_url = None
        if stage.image_key:
            image_url = s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": settings.AWS_STAGE_BUCKET,
                    "Key": stage.image_key,
                },
                ExpiresIn=60,
            )

        return success_response(
            message="스테이지 정보입니다.",
            data={
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

        return success_response(
            message="힌트 정보입니다.",
            data={
                "content": hint.content,
            },
        )