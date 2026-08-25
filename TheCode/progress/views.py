from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from commerce.entitlements import user_can_access_stage
from contents.models import Episode, Stage
from progress.models import UserEpisodeProgress
from utils.response import error_response, success_response


def get_first_released_episode():
    return (
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


def get_first_stage(episode):
    return episode.stages.order_by("stage_no").first()


class ProgressStartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        progress = (
            UserEpisodeProgress.objects.filter(
                user=request.user,
                episode__is_released=True,
                episode__series__is_active=True,
            )
            .select_related("episode")
            .order_by("-started_at")
            .first()
        )

        if progress:
            stage_exists = Stage.objects.filter(
                episode=progress.episode,
                stage_no=progress.current_stage_no,
            ).exists()
            if stage_exists:
                return success_response(
                    message="Progress start stage information.",
                    data={
                        "episode_id": progress.episode_id,
                        "episode_code": progress.episode.code,
                        "stage_no": progress.current_stage_no,
                        "highest_stage_no": progress.highest_stage_no,
                    },
                )

        episode = get_first_released_episode()
        if not episode:
            return error_response("Released episode does not exist.", status=404)

        stage = get_first_stage(episode)
        if not stage:
            return error_response("Start stage does not exist.", status=404)

        progress, _ = UserEpisodeProgress.objects.get_or_create(
            user=request.user,
            episode=episode,
            defaults={
                "current_stage_no": stage.stage_no,
                "highest_stage_no": stage.stage_no,
            },
        )

        return success_response(
            message="Progress start stage information.",
            data={
                "episode_id": episode.id,
                "episode_code": episode.code,
                "stage_no": progress.current_stage_no,
                "highest_stage_no": progress.highest_stage_no,
            },
        )


class CompleteStageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        episode_id = request.data.get("episode_id")
        stage_no = request.data.get("stage_no")

        if not episode_id or not stage_no:
            return error_response("episode_id and stage_no are required.", status=400)

        try:
            stage = Stage.objects.select_related("episode").get(
                episode_id=episode_id,
                stage_no=stage_no,
            )
        except Stage.DoesNotExist:
            return error_response("Stage does not exist.", status=404)

        if not user_can_access_stage(request.user, stage):
            return error_response("Premium stage access is required.", status=403)

        next_stage = (
            Stage.objects.filter(
                episode_id=episode_id,
                stage_no__gt=stage.stage_no,
            )
            .order_by("stage_no")
            .first()
        )

        next_stage_no = next_stage.stage_no if next_stage else stage.stage_no
        highest_stage_no = next_stage_no if next_stage else stage.stage_no

        progress, _ = UserEpisodeProgress.objects.get_or_create(
            user=request.user,
            episode=stage.episode,
            defaults={
                "current_stage_no": stage.stage_no,
                "highest_stage_no": stage.stage_no,
            },
        )

        progress.highest_stage_no = max(progress.highest_stage_no, highest_stage_no)
        progress.current_stage_no = next_stage_no
        if next_stage is None:
            progress.is_cleared = True
            progress.cleared_at = progress.cleared_at or timezone.now()
        progress.save(
            update_fields=[
                "current_stage_no",
                "highest_stage_no",
                "is_cleared",
                "cleared_at",
            ]
        )

        return success_response(
            message="Stage progress updated.",
            data={
                "episode_id": stage.episode_id,
                "episode_code": stage.episode.code,
                "stage_no": stage.stage_no,
                "next_stage_no": next_stage.stage_no if next_stage else None,
                "current_stage_no": progress.current_stage_no,
                "highest_stage_no": progress.highest_stage_no,
                "is_cleared": progress.is_cleared,
            },
        )
