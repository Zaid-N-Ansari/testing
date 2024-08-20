from django.urls import path
from .views import (
	IndexChatView,
	PersonalChatView,
	GroupChatView
)

app_name = 'chat'

urlpatterns = [
	path('', IndexChatView.as_view(), name='index'),
	path('personal/', PersonalChatView.as_view(), name='personal'),
	path('group/', GroupChatView.as_view(), name='group'),
]