from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from asgiref.sync import sync_to_async
from django.views import View
from django.views.generic.detail import DetailView
from account.models import UserAccount
from .models import Friend, FriendRequest, Notification


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

            FriendRequest.objects.get_or_create(from_user=from_user, to_user=to_user)

        except Exception as e:
            return JsonResponse({'result': 'An Unexpected Error has Occured'})

        else:
            return JsonResponse({ 'result': 'success'})

class Unfriend(View):
    http_method_names = ['post']
    async def post(self, request, *args, **kwargs):
        user = request.POST.get('friend')
        try:
            from_user = await UserAccount.objects.aget(username=request.user)
            to_user = await UserAccount.objects.aget(username=user)

            friend_instance = await Friend.objects.aget_or_create(user=from_user)
            friend_instance = friend_instance[0]
            await friend_instance.remove_friend(to_user)

            friend_instance = await Friend.objects.aget_or_create(user=to_user)
            friend_instance = friend_instance[0]
            await friend_instance.remove_friend(from_user)

        except Exception as e:
            print(e)
            return JsonResponse({'result': 'An Unexpected Error has Occurred'})

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

    async def post(self, request, *args, **kwargs):
        user = request.POST.get('user')
        try:
            print(request.POST)
            user = await UserAccount.objects.filter(username=user).afirst()
            fr = await FriendRequest.objects.filter(from_user=user).afirst()
            notif = await Notification.objects.filter(from_user=user).afirst()
            notif.type = 'regular_notification'
            fr.accept()
            notif.save()
            fr.delete()
        except Exception as e:
            print(e)
            return JsonResponse({'result': 'An Unexpected Error has Occured'})

        else:
            return JsonResponse({'result': 'success'})

class RejectFriendRequest(View):
    http_method_names = ['post']

    async def post(self, request, *args, **kwargs):
        user = request.POST.get('friend')
        try:
            from_user = await UserAccount.objects.aget(username=user)
            to_user = await UserAccount.objects.aget(username=request.user)

            fr = await FriendRequest.objects.aget(from_user=from_user, to_user=to_user)

            # await sync_to_async(fr.reject)()

        except Exception as e:
            print(e)
            return JsonResponse({'result': 'An Unexpected Error has Occured'})

        else:
            return JsonResponse({ 'result': 'success'})
