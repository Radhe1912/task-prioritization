from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Task
from .serializers import TaskInputSerializer, TaskOutputSerializer
from .services import PriorityCalculator

_calculator = PriorityCalculator()


def _validate_task_list(raw_tasks: list) -> tuple[list, list]:
    valid, invalid = [], []

    for raw_task in raw_tasks:
        serializer = TaskInputSerializer(data=raw_task)
        if serializer.is_valid():
            valid.append(serializer.validated_data)
        else:
            invalid.append({"task": raw_task, "errors": serializer.errors})

    return valid, invalid


class HealthCheckView(APIView):

    def get(self, request):
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class TaskValidationView(APIView):

    def post(self, request):
        if not isinstance(request.data, list):
            return Response(
                {"error": "Request body must be a JSON array of task objects."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        valid, invalid = _validate_task_list(request.data)

        return Response(
            {
                "valid_count": len(valid),
                "invalid_count": len(invalid),
                "valid": valid,
                "invalid": invalid,
            },
            status=status.HTTP_200_OK,
        )


class TaskPrioritizationView(APIView):

    def post(self, request):
        if not isinstance(request.data, list):
            return Response(
                {"error": "Request body must be a JSON array of task objects."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        valid_tasks, invalid_tasks = _validate_task_list(request.data)
        prioritized = []

        for task_data in valid_tasks:
            score, category = _calculator.calculate(task_data)

            task_obj, _ = Task.objects.update_or_create(
                title=task_data["title"],
                deadline_days=task_data["deadline_days"],
                estimated_hours=task_data["estimated_hours"],
                importance=task_data["importance"],
                defaults={
                    "priority_score": score,
                    "priority_category": category,
                },
            )

            prioritized.append(TaskOutputSerializer(task_obj).data)

        prioritized.sort(key=lambda t: t["priority_score"], reverse=True)

        return Response(
            {
                "prioritized": prioritized,
                "prioritized_count": len(prioritized),
                "invalid": invalid_tasks,
                "invalid_count": len(invalid_tasks),
            },
            status=status.HTTP_200_OK,
        )

class TaskListView(APIView):

    def get(self, request):
        tasks = Task.objects.all()
        serializer = TaskOutputSerializer(tasks, many=True)
        return Response(
            {"count": tasks.count(), "tasks": serializer.data},
            status=status.HTTP_200_OK,
        )
