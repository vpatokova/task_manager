from django.urls import path

from tasks import consumers

websocket_urlpatterns = [path("tasks/", consumers.TasksConsumer.as_asgi())]
