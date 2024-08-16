from django.urls import path
from .views import IndexChatView, ChatView

app_name = 'chat'

urlpatterns = [
	path('', IndexChatView.as_view(), name='index'),
	path('<str:username>', ChatView.as_view(), name='chat'),
]