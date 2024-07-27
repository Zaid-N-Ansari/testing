from django.urls import path
from .views import AddFriend, FriendsView, Unfriend

app_name = 'friend'

urlpatterns = [
	path('', FriendsView.as_view(), name='all'),
	path('unfriend/<str:username>', Unfriend.as_view(), name='unfriend'),
	path('addfriend/<str:username>', AddFriend.as_view(), name='addfriend'),
]