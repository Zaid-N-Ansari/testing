from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic.detail import DetailView
from account.models import UserAccount
from friend.models import Friend

class FriendsView(DetailView):
    model = UserAccount
    template_name = 'friend/friends.html'
    context_object_name = 'user'
    
    def get_object(self, queryset=None):
        return get_object_or_404(UserAccount, username=self.request.user.username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        friend_instance = get_object_or_404(Friend, user=self.object)
        context['friends'] = friend_instance.friends.all()
        return context

class Unfriend(View):
    pass