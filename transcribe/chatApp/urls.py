from django.urls import path
from .views import CreateRoom, MessageView


app_name = 'chatApp' 

urlpatterns = [
    path('', CreateRoom, name='create-room'),
    path('<str:room_name>/<str:username>/', MessageView, name='room'),
]
