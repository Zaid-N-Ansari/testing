from django.urls import path
from .views import (
	AddFriend,
	Unfriend,
	FriendsView,
	AcceptFriendRequest,
	RejectFriendRequest,
	CancelFriendRequest,
	Notifications,
)

app_name = 'friend'

urlpatterns = [
	path('', FriendsView.as_view(), name='all'),
	path('unfriend/', Unfriend.as_view(), name='unfriend'),
	path('addfriend/', AddFriend.as_view(), name='addfriend'),
	path('accept/', AcceptFriendRequest.as_view(), name='accept'),
	path('reject/', RejectFriendRequest.as_view(), name='reject'),
	path('cancel/', CancelFriendRequest.as_view(), name='cancel'),
	path('notifications/', Notifications.as_view(), name='notifications'),
]