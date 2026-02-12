from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Task(models.Model):
    task_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    deadline_days = models.IntegerField(validators=[MinValueValidator(0)])
    estimated_hours = models.FloatField(validators=[MinValueValidator(0.0)])
    importance = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=1,
    )

    priority_score = models.FloatField(default=0.0)
    priority_category = models.CharField(max_length=20, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ["-priority_score"]

    def __str__(self):
        return f"{self.title} [{self.priority_category}] (score={self.priority_score})"