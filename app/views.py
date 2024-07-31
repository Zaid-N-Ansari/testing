from django.views.generic import TemplateView

from account.models import UserAccount
from friend.models import FriendRequest

class HomeView(TemplateView):
    template_name = 'app/home.html'
    