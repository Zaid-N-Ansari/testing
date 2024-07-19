from django.urls import path
from .views import FriendsView

app_name = 'friend'

urlpatterns = [
	path('', FriendsView.as_view(), name='all'),
]