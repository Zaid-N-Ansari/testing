from django.urls import path
from .consumers import NotificationConsumer

notification_websocket_urlpatterns = [
    path('ws/notifications/', NotificationConsumer.as_asgi()),
]