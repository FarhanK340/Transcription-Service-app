"""
ASGI config for transcribe project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from liveTranscription import routing as live_routing
from chatApp import routing as chat_routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transcribe.settings')

# Initialize Django ASGI application to ensure settings are laoded
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(URLRouter(
        live_routing.websocket_urlpatterns +
        chat_routing.websocket_urlpatterns
    ))
})
