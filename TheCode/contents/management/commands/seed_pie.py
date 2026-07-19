import json
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from contents.models import Episode, Hint, Series, Stage


class Command(BaseCommand):
    help = "Seed PIE series, episode, stages, hints, and local media from a JSON manifest."

    def add_arguments(self, parser):
        parser.add_argument(
            "manifest",
            help="Path to the private PIE manifest JSON, for example ../PIE_Q/pie_episode_001.json.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate the manifest and source images without writing files or DB rows.",
        )

    def handle(self, *args, **options):
        manifest_path = Path(options["manifest"]).expanduser().resolve()
        dry_run = options["dry_run"]

        if not manifest_path.exists():
            raise CommandError(f"Manifest does not exist: {manifest_path}")

        manifest = self._load_manifest(manifest_path)
        base_dir = manifest_path.parent
        assets = manifest["assets"]
        question_dir = self._resolve_asset_dir(base_dir, assets["question_dir"])
        media_prefix = assets["media_prefix"].strip("/")
        media_target_dir = Path(settings.MEDIA_ROOT) / media_prefix

        self._validate_images(manifest, question_dir)

        if dry_run:
            self.stdout.write(self.style.SUCCESS("Dry run passed. No files or DB rows were changed."))
            return

        media_target_dir.mkdir(parents=True, exist_ok=True)

        with transaction.atomic():
            series = self._upsert_series(manifest["series"])
            episode = self._upsert_episode(series, manifest["episode"])
            stages = self._upsert_stages(
                episode=episode,
                stages_data=manifest["stages"],
                question_dir=question_dir,
                media_target_dir=media_target_dir,
                media_prefix=media_prefix,
            )
            self._link_next_stages(stages)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded series={series.code}, episode={episode.code}, stages={len(stages)}"
            )
        )

    def _load_manifest(self, manifest_path):
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CommandError(f"Invalid JSON: {exc}") from exc

        for key in ("series", "episode", "assets", "stages"):
            if key not in manifest:
                raise CommandError(f"Manifest is missing required key: {key}")

        if not isinstance(manifest["stages"], list) or not manifest["stages"]:
            raise CommandError("Manifest stages must be a non-empty list.")

        return manifest

    def _resolve_asset_dir(self, base_dir, asset_dir):
        path = Path(asset_dir).expanduser()
        if not path.is_absolute():
            path = base_dir / path
        return path.resolve()

    def _validate_images(self, manifest, question_dir):
        if not question_dir.exists():
            raise CommandError(f"Question image directory does not exist: {question_dir}")

        seen_stage_numbers = set()
        for stage_data in manifest["stages"]:
            stage_no = stage_data.get("stage_no")
            if not stage_no:
                raise CommandError("Every stage must have stage_no.")
            if stage_no in seen_stage_numbers:
                raise CommandError(f"Duplicate stage_no: {stage_no}")
            seen_stage_numbers.add(stage_no)

            answer_text = str(stage_data.get("answer_text", "")).strip()
            hint = str(stage_data.get("hint", "")).strip()
            if not answer_text or answer_text.startswith("TODO_"):
                raise CommandError(f"Stage {stage_no} answer_text is not filled.")
            if not hint or hint.startswith("TODO_"):
                raise CommandError(f"Stage {stage_no} hint is not filled.")

            question_image = stage_data.get("question_image")
            if not question_image:
                raise CommandError(f"Stage {stage_no} question_image is required.")

            source = question_dir / question_image
            if not source.exists():
                raise CommandError(f"Stage {stage_no} question image is missing: {source}")

    def _upsert_series(self, series_data):
        series, _ = Series.objects.update_or_create(
            code=series_data["code"],
            defaults={
                "title": series_data["title"],
                "description": series_data.get("description", ""),
                "is_active": series_data.get("is_active", True),
            },
        )
        return series

    def _upsert_episode(self, series, episode_data):
        episode, _ = Episode.objects.update_or_create(
            series=series,
            code=episode_data["code"],
            defaults={
                "title": episode_data["title"],
                "description": episode_data.get("description", ""),
                "is_released": episode_data.get("is_released", True),
                "price_unlock_stages": episode_data.get("price_unlock_stages", 0),
                "price_unlock_with_adfree": episode_data.get("price_unlock_with_adfree", 0),
            },
        )
        return episode

    def _upsert_stages(self, episode, stages_data, question_dir, media_target_dir, media_prefix):
        stages = {}
        for stage_data in sorted(stages_data, key=lambda item: item["stage_no"]):
            question_image = stage_data["question_image"]
            source = question_dir / question_image
            target = media_target_dir / question_image
            shutil.copy2(source, target)

            image_key = f"{media_prefix}/{question_image}"
            stage, _ = Stage.objects.update_or_create(
                episode=episode,
                stage_no=stage_data["stage_no"],
                defaults={
                    "title": stage_data.get("title") or f"Stage {stage_data['stage_no']}",
                    "is_free": stage_data.get("is_free", False),
                    "image_key": image_key,
                    "answer_text": stage_data["answer_text"],
                },
            )
            Hint.objects.update_or_create(
                stage=stage,
                defaults={"content": stage_data["hint"]},
            )
            stages[stage.stage_no] = stage
        return stages

    def _link_next_stages(self, stages):
        ordered_numbers = sorted(stages)
        for index, stage_no in enumerate(ordered_numbers):
            stage = stages[stage_no]
            next_stage = stages.get(ordered_numbers[index + 1]) if index + 1 < len(ordered_numbers) else None
            if stage.next_stage_id != (next_stage.id if next_stage else None):
                stage.next_stage = next_stage
                stage.save(update_fields=["next_stage"])
