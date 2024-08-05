from django.urls import path
from .views import CreateSession, TranscriptionView

urlpatterns = [
    path('', CreateSession, name='create-session'),
    path('<str:session_name>/', TranscriptionView, name='session')
]