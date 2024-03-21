from django.urls import path

from tasks.views import (
    TaskCreateView,
    TaskDeleteView,
    TaskListView,
    TaskSuspendView,
    TaskTimeView,
)

app_name = "tasks"
urlpatterns = [
    path("create/", TaskCreateView.as_view(), name="create"),
    path("<int:pk>/delete/", TaskDeleteView.as_view(), name="delete"),
    path("list/", TaskListView.as_view(), name="list"),
    path("<int:pk>/suspend/", TaskSuspendView.as_view(), name="suspend"),
    path("time/", TaskTimeView.as_view(), name="time"),
]
