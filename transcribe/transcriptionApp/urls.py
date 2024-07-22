from django.urls import path
from .views import upload_audio, view_transcription


urlpatterns = [
    path('', upload_audio, name='upload_audio'),
    path('transcription/<int:pk>', view_transcription, name='transcription'),
]
