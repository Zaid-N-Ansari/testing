from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
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
    http_method_names = ['post']
    def post(self, request, *args, **kwargs):
        user = request.POST.get('friend')
        try:
            from_user = UserAccount.objects.get(username=request.user)
            to_user = UserAccount.objects.get(username=user)

            friend_instance = Friend.objects.get_or_create(user=from_user)[0]
            friend_instance.friends.remove(to_user)
            friend_instance.save()

            friend_instance = Friend.objects.get_or_create(user=to_user)[0]
            friend_instance.friends.remove(from_user)
            friend_instance.save()

        except Exception as e:
            return JsonResponse({'result':e})

        else:
            return JsonResponse({
                'result': 'success'
            })

class AddFriend(View):
    http_method_names = ['post']
    def post(self, request, *args, **kwargs):
        user = request.POST.get('friend')
        try:
            from_user = UserAccount.objects.get(username=request.user)
            to_user = UserAccount.objects.get(username=user)

            friend_instance = Friend.objects.get_or_create(user=from_user)[0]
            friend_instance.friends.add(to_user)
            friend_instance.save()

            friend_instance = Friend.objects.get_or_create(user=to_user)[0]
            friend_instance.friends.add(from_user)
            friend_instance.save()

        except Exception as e:
            return JsonResponse({'result':e})

        else:
            return JsonResponse({
                'result': 'success'
            })