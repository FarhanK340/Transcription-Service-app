from django.contrib import admin
from django.urls import path, include
from .views import manage_routing

urlpatterns = [
    path('admin/', admin.site.urls),
    path('transcribe/', include('transcriptionApp.urls')),
    path('chat/', include('chatApp.urls')),
    path('live/', include('liveTranscription.urls')),
    path('', manage_routing, name='manage_routing'),
]
