from django.urls import path
from accounts.consumers import NotificationConsumer
from accounts.middleware import JWTAuthMiddleware
from channels.routing import ProtocolTypeRouter, URLRouter

websocket_urlpatterns = [
    path('ws/notifications/', NotificationConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})