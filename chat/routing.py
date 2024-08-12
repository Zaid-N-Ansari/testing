from django.urls import path
from .consumers import ChatConsumer

chat_websocket_urlpatterns = [
    path('ws/chat/', ChatConsumer.as_asgi()),
]