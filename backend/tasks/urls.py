from django.urls import path
from .views import HealthCheckView, TaskListView, TaskPrioritizationView, TaskValidationView

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("tasks/validate/", TaskValidationView.as_view(), name="task-validate"),
    path("tasks/prioritize/", TaskPrioritizationView.as_view(), name="task-prioritize"),
    path("tasks/", TaskListView.as_view(), name="task-list"),
]