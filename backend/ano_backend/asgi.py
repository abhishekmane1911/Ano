"""
ASGI config for ano_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ano_backend.settings")

django_asgi_app = get_asgi_application()

# Import routing after Django setup
from chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns
from matchmaking.routing import websocket_urlpatterns as matchmaking_websocket_urlpatterns
from chat.middleware import JWTAuthMiddleware

# Combine all WebSocket URL patterns
websocket_urlpatterns = chat_websocket_urlpatterns + matchmaking_websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": JWTAuthMiddleware(URLRouter(websocket_urlpatterns)),
    }
)
