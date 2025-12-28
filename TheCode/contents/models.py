from django.db import models


class Series(models.Model):
    code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}"
    

class Episode(models.Model):
    series = models.ForeignKey(
        Series,
        on_delete=models.CASCADE,
        related_name="episodes",
    )
    code = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    is_released = models.BooleanField(default=False)

    price_unlock_stages = models.IntegerField()
    price_unlock_with_adfree = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("series", "code")

    def __str__(self):
        return f"{self.series} - {self.title}"


class Stage(models.Model):
    episode = models.ForeignKey(
        Episode,
        on_delete=models.CASCADE,
        related_name="stages",
    )

    stage_no = models.PositiveIntegerField()
    title = models.CharField(max_length=255)

    is_free = models.BooleanField(default=False)

    image_key = models.CharField(max_length=500)

    answer_text = models.CharField(max_length=255)
    next_stage = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="prev_stages",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("episode", "stage_no")
        ordering = ["stage_no"]

    def __str__(self):
        return f"{self.episode} | {self.stage_no}. {self.title}"


class Hint(models.Model):
    stage = models.OneToOneField(
        Stage,
        on_delete=models.CASCADE,
        related_name="hint",
    )
    content = models.TextField()

    def __str__(self):
        return f"Hint for {self.stage}"
