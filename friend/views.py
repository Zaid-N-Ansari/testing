from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic.detail import DetailView
from account.models import UserAccount
from .models import Friend, FriendRequest, Notification
from asgiref.sync import sync_to_async
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from django.utils import timezone as tz
from django.core.paginator import Paginator


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
            
            FriendRequest.objects.get(from_user=from_user, to_user=to_user).reject()

        except Exception as e:
            return JsonResponse({'result': 'An Unexpected Error has Occured'})

        else:
            return JsonResponse({ 'result': 'success'})

class Notifications(View):
    async def get(self, request, *args, **kwargs):
        user = request.user
        user = await UserAccount.objects.aget(username=user)

        page_number = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))

        unseen_count = await Notification.objects.filter(
            to_user=user, seen=False
        ).acount()

        notifications_qs = await sync_to_async(lambda: Notification.objects.filter( from_user=user).order_by('created_at'))()

        paginator = Paginator(notifications_qs, per_page)
        page = await sync_to_async(lambda: paginator.get_page(page_number))()
        res:list = []

        async for fr in page.object_list:
            action = await sync_to_async(lambda: fr.__str__())()
            to_user = await sync_to_async(lambda: fr.to_user)()
            from_user = await sync_to_async(lambda: fr.from_user)()
            created_at = await sync_to_async(lambda: fr.created_at)()
            created_at_local = tz.localtime(created_at)
            natday = naturalday(created_at_local)
            formatted_time = ''
            if natday == 'today':
                formatted_time = f', {naturaltime(created_at_local)}'
            else:
                formatted_time = f' at {created_at_local.strftime("%I:%M %p")}'
            res.append({
                'to_user': f'{from_user}',
                'from_user': f'{to_user}',
                'created_at': f'{natday}{formatted_time}',
                'action': f'{action}',
                'count': f'{unseen_count}'
            })

        pagination = {
            'total_pages': paginator.num_pages,
            'current_page': page.number
        }

        return await sync_to_async(lambda: JsonResponse({
            'result': res,
            'pagination': pagination
        }))()