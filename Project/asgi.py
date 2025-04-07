import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project.settings')
import django
django.setup()

# Czyszczenie starych rekordów przy starcie serwera:
from simulation.models import Node, ActiveConnection

# Usuwamy tylko wpisy ActiveConnection – to są tymczasowe dane połączeń
ActiveConnection.objects.all().delete()
# Zamiast usuwać węzły, ustawiamy ich status na offline, aby nie tracić historycznych danych (transmisji, eventlogów)
Node.objects.all().update(status="offline")
print("Wyczyszczono wpisy ActiveConnection oraz ustawiono status Node na offline.")

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import simulation.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            simulation.routing.websocket_urlpatterns
        )
    ),
})
