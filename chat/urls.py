from django.urls import path
from .views import ChatView

app_name = 'chat'

urlpatterns = [
	path('<str:username>', ChatView.as_view(), name='chat'),
]