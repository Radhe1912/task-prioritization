from rest_framework import serializers

from .models import Task


class TaskInputSerializer(serializers.Serializer):

    title = serializers.CharField(max_length=200)
    deadline_days = serializers.IntegerField(min_value=0)
    estimated_hours = serializers.FloatField(min_value=0.0)
    importance = serializers.IntegerField(min_value=1, max_value=10)

    def validate_title(self, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Title must not be blank.")
        return stripped

    def validate_estimated_hours(self, value: float) -> float:
        if value > 10_000:
            raise serializers.ValidationError(
                "estimated_hours exceeds the maximum allowed value (10,000)."
            )
        return value


class TaskOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "task_id",
            "title",
            "deadline_days",
            "estimated_hours",
            "importance",
            "priority_score",
            "priority_category",
        ]
        read_only_fields = fields