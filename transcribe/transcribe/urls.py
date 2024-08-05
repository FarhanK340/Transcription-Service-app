from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('transcribe/', include('transcriptionApp.urls')),
    path('chat/', include('chatApp.urls')),
    path('live/', include('liveTranscription.urls')),
]
