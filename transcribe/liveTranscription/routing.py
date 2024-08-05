from django.urls import path
from .consumers import AudioConsumer

websocket_urlpatterns = [
    path('ws/notification/<str:session_name>/', AudioConsumer.as_asgi()),
]