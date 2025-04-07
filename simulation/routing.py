# simulation/routing.py

from django.urls import path
from .consumers import NodeConsumer, MasterConsumer

websocket_urlpatterns = [
    path('ws/node/<str:node_id>/', NodeConsumer.as_asgi()),
    path('ws/master/', MasterConsumer.as_asgi()),
]
