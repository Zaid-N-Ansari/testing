from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic.detail import DetailView
from account.models import UserAccount
from .models import Friend, FriendRequest

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

class AddFriend(View):
    http_method_names = ['post']
    def post(self, request, *args, **kwargs):
        user = request.POST.get('friend')
        try:
            from_user = UserAccount.objects.get(username=request.user)
            to_user = UserAccount.objects.get(username=user)

            friend_instance = Friend.objects.get_or_create(user=from_user)[0]
            friend_instance.add_friend(to_user)
            friend_instance.save()

            friend_instance = Friend.objects.get_or_create(user=to_user)[0]
            friend_instance.add_friend(from_user)
            friend_instance.save()

        except Exception as e:
            return JsonResponse({'result': 'An Unexpected Error has Occured'})

        else:
            return JsonResponse({ 'result': 'success'})

class Unfriend(View):
    http_method_names = ['post']
    def post(self, request, *args, **kwargs):
        user = request.POST.get('friend')
        try:
            from_user = UserAccount.objects.get(username=request.user)
            to_user = UserAccount.objects.get(username=user)

            friend_instance = Friend.objects.get_or_create(user=from_user)[0]
            friend_instance.remove_friend(to_user)
            friend_instance.save()

            friend_instance = Friend.objects.get_or_create(user=to_user)[0]
            friend_instance.remove_friend(from_user)
            friend_instance.save()

        except Exception as e:
            return JsonResponse({'result': 'An Unexpected Error has Occured'})

        else:
            return JsonResponse({'result': 'success'})

class CancelFriendRequest(View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        user = request.POST.get('friend')
        try:
            from_user = UserAccount.objects.get(username=request.user)
            to_user = UserAccount.objects.get(username=user)

            FriendRequest.objects.get(from_user=from_user, to_user=to_user).delete()

        except Exception as e:
            print(e)
            return JsonResponse({'result': 'An Unexpected Error has Occured'})

        else:
            return JsonResponse({'result': 'success'})


class AcceptFriendRequest(View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        user = request.POST.get('friend')
        try:
            from_user = UserAccount.objects.get(username=request.user)
            to_user = UserAccount.objects.get(username=user)

            FriendRequest.objects.create(from_user=from_user, to_user=to_user).save()

        except Exception as e:
            print(e)
            return JsonResponse({'result': 'An Unexpected Error has Occured'})

        else:
            return JsonResponse({'result': 'success'})

class RejectFriendRequest(View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        user = request.POST.get('friend')
        try:
            from_user = UserAccount.objects.get(username=request.user)
            to_user = UserAccount.objects.get(username=user)
            
            FriendRequest.objects.get(from_user=from_user, to_user=to_user).reject()()

        except Exception as e:
            return JsonResponse({'result': 'An Unexpected Error has Occured'})

        else:
            return JsonResponse({ 'result': 'success'})