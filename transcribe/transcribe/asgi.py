"""
ASGI config for transcribe project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from chatApp import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transcribe.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': URLRouter(
        routing.websocket_urlpatterns
    )
})
