from django.urls import path
from .views import HealthCheckView, TaskPrioritizationView, TaskValidationView

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("tasks/validate/", TaskValidationView.as_view(), name="task-validate"),
    path("tasks/prioritize/", TaskPrioritizationView.as_view(), name="task-prioritize"),
]