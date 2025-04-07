
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import simulation.routing  # import naszego routingu dla websocketów

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project.settings')
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            simulation.routing.websocket_urlpatterns
        )
    ),
})


