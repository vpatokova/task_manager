import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from tasks import routing as tasks_routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_manager.settings")
django_asgi_app = get_asgi_application()
application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    [
                        *tasks_routing.websocket_urlpatterns,
                    ]
                ),
            ),
        ),
    }
)
