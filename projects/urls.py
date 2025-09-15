from django.urls import path
from .views import clickup_tasks
from .views import clickup_tasks, set_clickup_token

app_name = "projects"

urlpatterns = [
    path("", clickup_tasks, name="clickup_tasks"),
    path("set-token/", set_clickup_token, name="set_clickup_token"),
]