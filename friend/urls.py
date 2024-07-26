from django.urls import path
from .views import FriendsView, Unfriend

app_name = 'friend'

urlpatterns = [
	path('', FriendsView.as_view(), name='all'),
	path('unfriend/', Unfriend.as_view(), name='unfriend'),
]