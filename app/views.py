from django.views.generic import TemplateView

from account.models import UserAccount
from friend.models import FriendRequest

class HomeView(TemplateView):
    template_name = 'app/home.html'
    def get_context_data(self, **kwargs) -> dict[str, any]:
        context = super().get_context_data(**kwargs)
        context["infos"] = FriendRequest.get_all_from_user('test.user2')
        print(context['infos'])
        return context
    